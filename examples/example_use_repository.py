"""
Example: Using scrapers from the repository
"""
from scraper_repository import get_scraper, get_scraper_for_url, list_scrapers


def example_1_get_by_domain():
    """Example 1: Get scraper by domain name"""
    print("=" * 60)
    print("Example 1: Get scraper by domain")
    print("=" * 60)
    
    try:
        # Get scraper for Harvard Medical School
        scraper = get_scraper("hms.harvard.edu")
        
        # Use it to scrape a URL
        url = "https://hms.harvard.edu/news/ai-system-detailed-diagnostic-reasoning-makes-its-case"
        data = scraper.scrape(url)
        
        print(f"\nScraped data from {url}:")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Author: {data.get('author', 'N/A')}")
        print(f"Date: {data.get('publish_date', 'N/A')}")
        print(f"Content preview: {data.get('content', '')[:100]}...")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Scraper not found. Generate it first using ADK Web.")


def example_2_auto_detect():
    """Example 2: Auto-detect scraper from URL"""
    print("\n" + "=" * 60)
    print("Example 2: Auto-detect scraper from URL")
    print("=" * 60)
    
    try:
        url = "https://hms.harvard.edu/news/some-article"
        
        # Automatically find the right scraper
        scraper = get_scraper_for_url(url)
        data = scraper.scrape(url)
        
        print(f"\nAuto-detected scraper for: {url}")
        print(f"Extracted fields: {list(data.keys())}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")


def example_3_list_all():
    """Example 3: List all available scrapers"""
    print("\n" + "=" * 60)
    print("Example 3: List all available scrapers")
    print("=" * 60)
    
    scrapers = list_scrapers()
    
    if not scrapers:
        print("\nNo scrapers in repository yet.")
        print("Generate some using ADK Web first!")
    else:
        print(f"\nFound {len(scrapers)} scraper(s):\n")
        for scraper in scrapers:
            print(f"Domain: {scraper['domain']}")
            print(f"  Site: {scraper.get('site_name', 'N/A')}")
            print(f"  Fields: {', '.join(scraper.get('fields', []))}")
            print(f"  Created: {scraper.get('created_at', 'N/A')}")
            print(f"  Example URL: {scraper.get('example_url', 'N/A')}")
            print()


def example_4_batch_scraping():
    """Example 4: Batch scraping multiple URLs"""
    print("\n" + "=" * 60)
    print("Example 4: Batch scraping multiple URLs")
    print("=" * 60)
    
    urls = [
        "https://hms.harvard.edu/news/article-1",
        "https://hms.harvard.edu/news/article-2",
        "https://hms.harvard.edu/news/article-3",
    ]
    
    try:
        scraper = get_scraper("hms.harvard.edu")
        
        print(f"\nScraping {len(urls)} URLs...\n")
        results = []
        
        for url in urls:
            try:
                data = scraper.scrape(url)
                results.append(data)
                print(f"✓ {url}")
            except Exception as e:
                print(f"✗ {url}: {e}")
        
        print(f"\nSuccessfully scraped {len(results)} URLs")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCRAPER REPOSITORY USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    example_3_list_all()  # Start by showing what's available
    example_1_get_by_domain()
    example_2_auto_detect()
    example_4_batch_scraping()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
