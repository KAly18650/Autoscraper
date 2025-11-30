"""
Example: Using scraper pipelines (list + content scrapers)
"""
from scraper_repository import (
    get_scraper_pipeline, 
    has_scraper_pipeline,
    list_scraper_pipelines
)


def example_1_check_pipeline_exists():
    """Example 1: Check if a domain has a complete pipeline"""
    print("=" * 60)
    print("Example 1: Check if pipeline exists")
    print("=" * 60)
    
    domain = "hms.harvard.edu"
    
    if has_scraper_pipeline(domain):
        print(f"✓ Complete pipeline exists for {domain}")
        print("  - List scraper: Gets URLs from listing pages")
        print("  - Content scraper: Extracts data from individual articles")
    else:
        print(f"✗ No complete pipeline for {domain}")
        print("  Generate both scrapers using ADK Web first!")


def example_2_use_pipeline():
    """Example 2: Use a complete scraper pipeline"""
    print("\n" + "=" * 60)
    print("Example 2: Use scraper pipeline")
    print("=" * 60)
    
    try:
        # Get both scrapers
        list_scraper, content_scraper = get_scraper_pipeline("hms.harvard.edu")
        
        # Step 1: Get list of URLs
        listing_url = "https://hms.harvard.edu/news"
        print(f"\nStep 1: Getting URLs from {listing_url}")
        urls_data = list_scraper.scrape(listing_url)
        urls = urls_data.get("urls", [])
        print(f"Found {len(urls)} URLs")
        
        # Step 2: Scrape first 3 articles
        print(f"\nStep 2: Scraping first 3 articles...")
        articles = []
        for i, url in enumerate(urls[:3]):
            try:
                print(f"\n  [{i+1}] Scraping: {url}")
                article_data = content_scraper.scrape(url)
                articles.append(article_data)
                print(f"      Title: {article_data.get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"      Error: {e}")
        
        print(f"\n✓ Successfully scraped {len(articles)} articles")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Generate the pipeline using ADK Web first!")


def example_3_list_all_pipelines():
    """Example 3: List all available pipelines"""
    print("\n" + "=" * 60)
    print("Example 3: List all available pipelines")
    print("=" * 60)
    
    pipelines = list_scraper_pipelines()
    
    if not pipelines:
        print("\nNo complete pipelines found.")
        print("Generate some using ADK Web first!")
    else:
        print(f"\nFound {len(pipelines)} complete pipeline(s):\n")
        for pipeline in pipelines:
            print(f"Domain: {pipeline['domain']}")
            print(f"  Site: {pipeline.get('site_name', 'N/A')}")
            print(f"  List Scraper:")
            print(f"    - Example: {pipeline['list_scraper']['example_url']}")
            print(f"    - Created: {pipeline['list_scraper']['created_at']}")
            print(f"  Content Scraper:")
            print(f"    - Example: {pipeline['content_scraper']['example_url']}")
            print(f"    - Fields: {', '.join(pipeline['content_scraper']['fields'])}")
            print(f"    - Created: {pipeline['content_scraper']['created_at']}")
            print()


def example_4_full_workflow():
    """Example 4: Complete workflow - list all articles and scrape them"""
    print("\n" + "=" * 60)
    print("Example 4: Full workflow - scrape all articles")
    print("=" * 60)
    
    try:
        list_scraper, content_scraper = get_scraper_pipeline("hms.harvard.edu")
        
        # Get all URLs
        listing_url = "https://hms.harvard.edu/news"
        print(f"\nGetting all URLs from {listing_url}...")
        urls_data = list_scraper.scrape(listing_url)
        urls = urls_data.get("urls", [])
        print(f"Found {len(urls)} URLs")
        
        # Scrape all articles (with error handling)
        print(f"\nScraping all {len(urls)} articles...")
        articles = []
        errors = 0
        
        for i, url in enumerate(urls):
            try:
                article_data = content_scraper.scrape(url)
                articles.append(article_data)
                print(f"  [{i+1}/{len(urls)}] ✓ {url}")
            except Exception as e:
                errors += 1
                print(f"  [{i+1}/{len(urls)}] ✗ {url}: {e}")
        
        print(f"\n{'='*60}")
        print(f"Results:")
        print(f"  Total URLs: {len(urls)}")
        print(f"  Successfully scraped: {len(articles)}")
        print(f"  Errors: {errors}")
        print(f"  Success rate: {len(articles)/len(urls)*100:.1f}%")
        
        # Show sample data
        if articles:
            print(f"\nSample article:")
            sample = articles[0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCRAPER PIPELINE USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    example_3_list_all_pipelines()  # Start by showing what's available
    example_1_check_pipeline_exists()
    example_2_use_pipeline()
    example_4_full_workflow()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
