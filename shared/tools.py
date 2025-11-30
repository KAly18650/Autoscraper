"""
Shared tools used by all agents.
"""

import requests
import subprocess
import sys
import tempfile
import os
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
from .scraper_saver import save_scraper as _save_scraper
from .logger import get_logger

logger = get_logger(__name__)


def _fetch_and_parse_sync(url: str) -> Tuple[BeautifulSoup, str]:
    """
    Synchronous helper: Fetches HTML using Playwright and returns BeautifulSoup object.
    Uses a headless browser to handle JavaScript-rendered content.
    
    Args:
        url: The URL to fetch
        
    Returns:
        Tuple of (soup, error_message). If error, soup is None.
    """
    browser = None
    context = None
    page = None
    try:
        logger.info(f"Starting Playwright for URL: {url}")
        with sync_playwright() as p:
            logger.info("Launching Chromium browser with stealth args")
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-blink-features=AutomationControlled'  # Hide automation
                ]
            )
            logger.info("Browser launched successfully")
            
            # Create context with more realistic settings
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            page = context.new_page()
            
            # Mask webdriver property
            await_js = """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            page.add_init_script(await_js)
            logger.info(f"New page created, navigating to: {url}")
            
            # Try networkidle first, fall back to domcontentloaded if it fails
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                logger.info("Page navigation completed (networkidle)")
            except Exception as nav_error:
                logger.warning(f"networkidle failed: {nav_error}, retrying with domcontentloaded")
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                # Give it a moment for JS to execute
                page.wait_for_timeout(2000)
                logger.info("Page navigation completed (domcontentloaded + 2s wait)")
            
            html_content = page.content()
            logger.info(f"Retrieved HTML content: {len(html_content)} chars")
            
            browser.close()
            logger.info("Browser closed successfully")
            
        if not html_content or len(html_content) < 100:
            return None, f"Retrieved HTML is too short ({len(html_content)} chars). Page may have failed to load."
            
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup, None
    except PlaywrightTimeoutError as e:
        logger.error(f"Playwright timeout error: {str(e)}")
        return None, "Timeout: Page took too long to load (30s). The site may be slow or blocking automated access."
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Playwright error during fetch: {error_msg}", exc_info=True)
        if "Executable doesn't exist" in error_msg or "browser executable" in error_msg.lower():
            return None, "Playwright browsers not installed. Run: playwright install chromium"
        return None, f"Error fetching page: {error_msg}"
    finally:
        # Ensure cleanup even if there's an error
        try:
            if page:
                page.close()
            if browser:
                browser.close()
        except Exception as cleanup_error:
            logger.warning(f"Error during cleanup: {cleanup_error}")


async def _fetch_and_parse(url: str) -> Tuple[BeautifulSoup, str]:
    """
    Async wrapper: Runs sync Playwright in a thread pool to avoid Windows subprocess issues.
    """
    return await asyncio.to_thread(_fetch_and_parse_sync, url)


async def test_selector(url: str, selector: str, attribute: str = "") -> str:
    """
    Tests a CSS selector on a URL and shows what it finds.
    Helps the analyst verify selectors before generating the full Selector Map.
    
    Args:
        url: The URL to test against
        selector: The CSS selector to test (e.g., "h1.title", "article.content")
        attribute: Optional attribute to extract (e.g., "href", "datetime"). Leave empty for text content.
        
    Returns:
        A report showing what the selector matched and the extracted data
    """
    logger.info(f"Tool invoked: test_selector(url={url}, selector={selector}, attribute={attribute})")
    soup, error = await _fetch_and_parse(url)
    if error or soup is None:
        msg = f"❌ Error fetching webpage: {error or 'Unknown error - soup is None'}"
        logger.warning(msg)
        return msg
    
    try:
        
        report = f"Testing selector: '{selector}' on {url}\n"
        report += "=" * 80 + "\n\n"
        
        # Try select_one (single element)
        element = soup.select_one(selector)
        if element:
            report += f"✓ Found 1 element with select_one()\n"
            report += f"  Tag: <{element.name}>\n"
            report += f"  Classes: {element.get('class', [])}\n"
            report += f"  ID: {element.get('id', 'N/A')}\n"
            
            if attribute and attribute.strip():
                value = element.get(attribute)
                report += f"  Attribute '{attribute}': {value}\n"
            else:
                text = element.get_text(strip=True)
                report += f"  Text (first 200 chars): {text[:200]}\n"
                report += f"  Text length: {len(text)} characters\n"
        else:
            report += f"✗ No element found with select_one()\n"
        
        # Try select (multiple elements)
        elements = soup.select(selector)
        report += f"\n{len(elements)} total elements found with select()\n"
        
        if elements and len(elements) > 1:
            report += "\nFirst 3 matches:\n"
            for i, elem in enumerate(elements[:3]):
                text = elem.get_text(strip=True)
                report += f"  [{i+1}] {text[:100]}...\n"
        
        return report
    except Exception as e:
        return f"Error testing selector: {str(e)}"


async def analyze_html_structure(url: str) -> str:
    """
    Fetches a webpage and provides a structured analysis of its HTML.
    Helps identify the best selectors for scraping.
    
    Args:
        url: The URL to analyze
        
    Returns:
        A structured report of HTML elements and suggested selectors
    """
    logger.info(f"Tool invoked: analyze_html_structure(url={url})")
    soup, error = await _fetch_and_parse(url)
    if error or soup is None:
        msg = f"❌ Error fetching webpage: {error or 'Unknown error - soup is None'}"
        logger.warning(msg)
        return msg
    
    try:
        
        report = f"HTML Structure Analysis for: {url}\n"
        report += "=" * 80 + "\n\n"
        
        # Analyze main content containers
        report += "MAIN CONTENT CONTAINERS:\n"
        for tag in ['main', 'article', 'div[role="main"]']:
            elements = soup.select(tag)
            if elements:
                for i, elem in enumerate(elements[:3]):  # Limit to first 3
                    classes = ' '.join(elem.get('class', []))
                    id_attr = elem.get('id', '')
                    report += f"  - <{elem.name}> "
                    if id_attr:
                        report += f"id='{id_attr}' "
                    if classes:
                        report += f"class='{classes}' "
                    # Show first 100 chars of text
                    text_preview = elem.get_text(strip=True)[:100]
                    report += f"\n    Text preview: {text_preview}...\n"
        
        report += "\nHEADINGS (H1-H2):\n"
        for heading in soup.find_all(['h1', 'h2'])[:5]:
            classes = ' '.join(heading.get('class', []))
            report += f"  - <{heading.name}> class='{classes}': {heading.get_text(strip=True)}\n"
        
        report += "\nTIME/DATE ELEMENTS:\n"
        for time_elem in soup.find_all('time')[:3]:
            datetime_attr = time_elem.get('datetime', '')
            classes = ' '.join(time_elem.get('class', []))
            report += f"  - <time> class='{classes}' datetime='{datetime_attr}': {time_elem.get_text(strip=True)}\n"
        
        report += "\nAUTHOR-RELATED ELEMENTS:\n"
        # Check meta tags
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta:
            report += f"  - <meta name='author' content='{author_meta.get('content', '')}'/>\n"
        
        # Check for author-related classes
        for selector in ['.author', '.byline', '[rel="author"]', '.writer', '.post-author']:
            elements = soup.select(selector)
            if elements:
                for elem in elements[:2]:
                    report += f"  - {selector}: {elem.get_text(strip=True)}\n"
        
        report += "\nLARGE TEXT BLOCKS (potential content):\n"
        for tag in ['article', 'main', '.content', '.article-body', '.post-content', '.entry-content']:
            elements = soup.select(tag)
            for elem in elements[:2]:
                text = elem.get_text(strip=True)
                if len(text) > 200:  # Only show substantial content
                    classes = ' '.join(elem.get('class', []))
                    report += f"  - <{elem.name}> class='{classes}'\n"
                    report += f"    Length: {len(text)} chars\n"
                    report += f"    Preview: {text[:150]}...\n\n"
        
        return report
    except Exception as e:
        return f"Error analyzing HTML structure: {str(e)}"


def execute_code(code: str, test_url: str) -> dict:
    """
    Executes Python scraper code and returns the result.
    
    Args:
        code: The Python code to execute (must define a 'scrape' function)
        test_url: The URL to test the scraper against
        
    Returns:
        A dictionary with 'success' (bool), 'output' (str), and 'error' (str) keys
    """
    logger.info(f"Tool invoked: execute_code(test_url={test_url})")
    try:
        # Create a temporary file to execute the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # Remove any existing if __name__ == '__main__' block from the code
            # to avoid conflicts with our wrapper
            code_lines = code.split('\n')
            cleaned_code = []
            skip_main_block = False
            
            for line in code_lines:
                if "if __name__ ==" in line:
                    skip_main_block = True
                    continue
                if skip_main_block:
                    # Check if we're still in the main block
                    if line.strip() == "":
                        # Empty line - skip it
                        continue
                    elif line and line[0] not in (' ', '\t'):
                        # Non-indented line - we've exited the main block
                        skip_main_block = False
                        # Don't continue - process this line normally
                    else:
                        # Indented line - still in the main block, skip it
                        continue
                
                if not skip_main_block:
                    cleaned_code.append(line)
            
            code_cleaned = '\n'.join(cleaned_code)
            
            # Wrap the code to capture output
            wrapped_code = f"""{code_cleaned}

# Execute the scraper
if __name__ == '__main__':
    import json
    try:
        result = scrape('{test_url}')
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"EXECUTION_ERROR: {{str(e)}}")
"""
            f.write(wrapped_code)
            temp_file = f.name
        
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'  # Replace invalid UTF-8 bytes with �
        )
        
        # Clean up
        os.unlink(temp_file)
        
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        
        if result.returncode != 0 or "EXECUTION_ERROR" in output:
            return {
                "success": False,
                "output": output,
                "error": error or "Code execution failed",
                "debug_info": f"STDOUT:\n{output}\n\nSTDERR:\n{error}"
            }
        
        return {
            "success": True,
            "output": output,
            "error": "",
            "debug_info": f"STDOUT:\n{output}"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Code execution timed out (30s limit)"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }


def save_scraper_to_repository(code: str, url: str, selectors: dict, site_name: Optional[str] = None, scraper_type: str = "single") -> dict:
    """
    Save a validated scraper to the repository for reuse.
    
    Args:
        code: The Python scraper code
        url: The URL this scraper was designed for
        selectors: The selector map used
        site_name: Optional site name
        scraper_type: Type of scraper - "single" (default), "list", or "content"
        
    Returns:
        Dictionary with save status and paths
    """
    logger.info(f"Tool invoked: save_scraper_to_repository(domain={urlparse(url).netloc}, type={scraper_type})")
    try:
        result = _save_scraper(code, url, selectors, site_name, scraper_type)
        return {
            "success": True,
            "message": f"Scraper saved successfully for domain: {result['domain']} (type: {scraper_type})",
            "scraper_path": result['scraper_path'],
            "metadata_path": result['metadata_path'],
            "domain": result['domain'],
            "scraper_type": scraper_type
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to save scraper: {str(e)}"
        }
