"""
Scraper Repository - Auto-generated web scrapers for reuse
"""
import os
import json
import importlib.util
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import re
import sys
from pathlib import Path

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.storage import storage
from shared.logger import get_logger

logger = get_logger(__name__)

SCRAPERS_DIR = os.path.join(os.path.dirname(__file__), "scrapers")
METADATA_DIR = os.path.join(os.path.dirname(__file__), "metadata")


def _ensure_file_available(rel_path: str) -> str:
    """
    Ensure a file is available locally (fetching from GCS if needed).
    
    Args:
        rel_path: Relative path (e.g. 'scrapers/example_com.py')
        
    Returns:
        Absolute local path to the file
        
    Raises:
        FileNotFoundError: If file cannot be found
    """
    content = storage.read_content(rel_path)
    if content is None:
        raise FileNotFoundError(f"File not found in storage: {rel_path}")
        
    # Storage manager read_content already handles saving to local cache
    repo_root = os.path.dirname(__file__)
    return os.path.join(repo_root, rel_path)


def get_scraper(domain: str):
    """
    Get a scraper module by domain name.
    
    Args:
        domain: Domain name (e.g., "hms.harvard.edu")
        
    Returns:
        Scraper module with a scrape() function
        
    Raises:
        FileNotFoundError: If scraper doesn't exist
    """
    # Convert domain to filename (replace dots with underscores)
    filename = domain.replace(".", "_") + ".py"
    rel_path = f"scrapers/{filename}"
    
    try:
        filepath = _ensure_file_available(rel_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"No scraper found for domain: {domain}")
    
    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(f"scraper_{domain}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    logger.info(f"Loaded scraper for domain: {domain}")
    return module


def get_scraper_metadata(domain: str) -> Dict[str, Any]:
    """
    Get metadata for a scraper.
    
    Args:
        domain: Domain name (e.g., "hms.harvard.edu")
        
    Returns:
        Dictionary containing scraper metadata
    """
    filename = domain.replace(".", "_") + ".json"
    rel_path = f"metadata/{filename}"
    
    content = storage.read_content(rel_path)
    if not content:
        return {}
    
    return json.loads(content)


def get_scraper_for_url(url: str):
    """
    Auto-detect and return the appropriate scraper for a URL.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Scraper module with a scrape() function
        
    Raises:
        FileNotFoundError: If no matching scraper is found
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Try exact domain match first
    try:
        return get_scraper(domain)
    except FileNotFoundError:
        pass
    
    # Try pattern matching against all scrapers
    # Note: iterating GCS files is slow, we rely on list_files
    metadata_files = storage.list_files("metadata/")
    
    for metadata_file_path in metadata_files:
        if not metadata_file_path.endswith('.json'):
            continue
            
        content = storage.read_content(metadata_file_path)
        if not content:
            continue
            
        try:
            metadata = json.loads(content)
            url_pattern = metadata.get('url_pattern', '')
            if url_pattern and re.match(url_pattern, url):
                domain = metadata['domain']
                logger.info(f"Matched URL {url} to scraper for domain {domain}")
                return get_scraper(domain)
        except json.JSONDecodeError:
            logger.warning(f"Corrupt metadata file: {metadata_file_path}")
            continue
    
    raise FileNotFoundError(f"No scraper found for URL: {url}")


def list_scrapers() -> list:
    """
    List all available scrapers.
    
    Returns:
        List of dictionaries containing scraper info
    """
    scrapers = []
    metadata_files = storage.list_files("metadata/")
    
    for metadata_file_path in metadata_files:
        if not metadata_file_path.endswith('.json'):
            continue
            
        content = storage.read_content(metadata_file_path)
        if content:
            try:
                metadata = json.loads(content)
                scrapers.append(metadata)
            except json.JSONDecodeError:
                pass
    
    return scrapers


def get_scraper_pipeline(domain: str):
    """
    Get both list and content scrapers for a domain as a pipeline.
    """
    base_name = domain.replace(".", "_")
    list_rel = f"scrapers/{base_name}_list.py"
    content_rel = f"scrapers/{base_name}_content.py"
    
    try:
        list_path = _ensure_file_available(list_rel)
        content_path = _ensure_file_available(content_rel)
    except FileNotFoundError:
         raise FileNotFoundError(f"Incomplete pipeline for domain: {domain}")

    # Load list scraper
    list_spec = importlib.util.spec_from_file_location(f"scraper_{domain}_list", list_path)
    list_module = importlib.util.module_from_spec(list_spec)
    list_spec.loader.exec_module(list_module)
    
    # Load content scraper
    content_spec = importlib.util.spec_from_file_location(f"scraper_{domain}_content", content_path)
    content_module = importlib.util.module_from_spec(content_spec)
    content_spec.loader.exec_module(content_module)
    
    logger.info(f"Loaded scraper pipeline for {domain}")
    return list_module, content_module


def has_scraper_pipeline(domain: str) -> bool:
    """
    Check if a domain has both list and content scrapers.
    """
    base_name = domain.replace(".", "_")
    list_rel = f"scrapers/{base_name}_list.py"
    content_rel = f"scrapers/{base_name}_content.py"
    
    return storage.exists(list_rel) and storage.exists(content_rel)


def list_scraper_pipelines() -> list:
    """
    List all domains that have complete scraper pipelines (both list and content).
    """
    pipelines = []
    domains_seen = set()
    
    metadata_files = storage.list_files("metadata/")
    
    for metadata_file_path in metadata_files:
        if not metadata_file_path.endswith('.json'):
            continue
            
        content = storage.read_content(metadata_file_path)
        if not content:
            continue
            
        try:
            metadata = json.loads(content)
        except:
            continue
        
        scraper_type = metadata.get('scraper_type', 'single')
        domain = metadata.get('domain', '')
        
        if scraper_type == 'list' and domain and domain not in domains_seen:
            # Check if corresponding content scraper exists
            if has_scraper_pipeline(domain):
                domains_seen.add(domain)
                
                # Get content scraper metadata
                content_metadata_file = f"metadata/{domain.replace('.', '_')}_content.json"
                content_str = storage.read_content(content_metadata_file)
                
                content_metadata = {}
                if content_str:
                    content_metadata = json.loads(content_str)
                
                pipelines.append({
                    'domain': domain,
                    'site_name': metadata.get('site_name', domain),
                    'list_scraper': {
                        'example_url': metadata.get('example_url', ''),
                        'created_at': metadata.get('created_at', '')
                    },
                    'content_scraper': {
                        'example_url': content_metadata.get('example_url', ''),
                        'fields': content_metadata.get('fields', []),
                        'created_at': content_metadata.get('created_at', '')
                    }
                })
    
    return pipelines


__all__ = [
    'get_scraper', 
    'get_scraper_for_url', 
    'get_scraper_metadata', 
    'list_scrapers',
    'get_scraper_pipeline',
    'has_scraper_pipeline',
    'list_scraper_pipelines'
]
