"""
Utility to save validated scrapers to the repository
"""
import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from .storage import storage
from .logger import get_logger

logger = get_logger(__name__)


def domain_to_filename(domain: str) -> str:
    """Convert domain to valid filename"""
    return domain.replace(".", "_")


def save_scraper(
    code: str,
    url: str,
    selectors: Dict[str, Any],
    site_name: Optional[str] = None,
    scraper_type: str = "single"
) -> Dict[str, str]:
    """
    Save a validated scraper to the repository (and GCS if configured).
    
    Args:
        code: The Python scraper code
        url: The URL this scraper was designed for
        selectors: The selector map used
        site_name: Optional site name
        scraper_type: Type of scraper - "single", "list", or "content"
        
    Returns:
        Dictionary with 'scraper_path', 'metadata_path', and 'domain'
    """
    # Extract domain from URL
    parsed = urlparse(url)
    domain = parsed.netloc
    filename_base = domain_to_filename(domain)
    
    # Add type suffix for list/content scrapers
    if scraper_type in ["list", "content"]:
        filename_base = f"{filename_base}_{scraper_type}"
    
    # Define paths relative to repository root
    scraper_rel_path = f"scrapers/{filename_base}.py"
    metadata_rel_path = f"metadata/{filename_base}.json"
    
    # Save the scraper code
    storage.save_content(scraper_rel_path, code)
    logger.info(f"Saved scraper code for {domain} to {scraper_rel_path}")
    
    # Extract field names from selectors
    fields = list(selectors.keys()) if isinstance(selectors, dict) else []
    
    # Create metadata
    metadata = {
        "domain": domain,
        "site_name": site_name or domain,
        "scraper_type": scraper_type,
        "url_pattern": f"https?://{re.escape(domain)}/.*",
        "example_url": url,
        "fields": fields,
        "selectors": selectors,
        "created_at": datetime.now().isoformat(),
        "last_validated": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    # Save metadata
    storage.save_content(metadata_rel_path, json.dumps(metadata, indent=2, ensure_ascii=False))
    logger.info(f"Saved metadata for {domain} to {metadata_rel_path}")
    
    # Return local paths for backward compatibility/UI display
    repo_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scraper_repository")
    return {
        "scraper_path": os.path.join(repo_root, scraper_rel_path),
        "metadata_path": os.path.join(repo_root, metadata_rel_path),
        "domain": domain
    }


def update_scraper_validation(domain: str):
    """
    Update the last_validated timestamp for a scraper.
    
    Args:
        domain: Domain name
    """
    filename_base = domain_to_filename(domain)
    metadata_rel_path = f"metadata/{filename_base}.json"
    
    content = storage.read_content(metadata_rel_path)
    
    if not content:
        logger.warning(f"Could not find metadata for {domain} to update validation")
        return
    
    try:
        metadata = json.loads(content)
        metadata['last_validated'] = datetime.now().isoformat()
        storage.save_content(metadata_rel_path, json.dumps(metadata, indent=2, ensure_ascii=False))
        logger.info(f"Updated validation timestamp for {domain}")
    except Exception as e:
        logger.error(f"Failed to update validation timestamp for {domain}: {e}")
