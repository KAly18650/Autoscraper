"""
Test script for running scrapers from the scraper_repository.
"""
import json
import sys
from pathlib import Path

# Add scraper_repository to path
sys.path.insert(0, str(Path(__file__).parent / "scraper_repository" / "scrapers"))

def test_scraper(scraper_name: str, test_url: str):
    """
    Test a scraper from the repository.
    
    Args:
        scraper_name: Name of the scraper module (without .py)
        test_url: URL to test the scraper against
    """
    print(f"\n{'='*80}")
    print(f"Testing: {scraper_name}")
    print(f"URL: {test_url}")
    print(f"{'='*80}\n")
    
    try:
        # Import the scraper module
        scraper_module = __import__(scraper_name)
        
        # Run the scrape function
        result = scraper_module.scrape(test_url)
        
        # Display results
        print(f"\n{'='*80}")
        print("RESULTS:")
        print(f"{'='*80}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n{'='*80}\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test the Harvard Medical School scrapers
    
    # Test 1: List scraper (gets URLs from listing page)
    print("\n🔍 TEST 1: List Scraper")
    list_result = test_scraper(
        "hms_harvard_edu_list",
        "https://hms.harvard.edu/news"
    )
    
    # Test 2: Content scraper (gets article details)
    if list_result and list_result.get("urls"):
        print("\n🔍 TEST 2: Content Scraper")
        # Test on the first URL from the list
        first_url = list_result["urls"][0]
        test_scraper(
            "hms_harvard_edu_content",
            first_url
        )
    
    print("\n✅ Testing complete!")
