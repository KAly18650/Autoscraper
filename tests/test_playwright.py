"""
Diagnostic script to test if Playwright is working correctly.
Run this to verify Playwright installation and browser access.
"""
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def test_playwright():
    """Test Playwright installation and basic functionality."""
    print("=" * 80)
    print("PLAYWRIGHT DIAGNOSTIC TEST")
    print("=" * 80)
    
    # Test 1: Check if Playwright can be imported
    print("\n✓ Test 1: Playwright module imported successfully")
    
    # Test 2: Try to launch browser
    print("\n⏳ Test 2: Attempting to launch Chromium browser...")
    try:
        async with async_playwright() as p:
            print("  - Playwright context created")
            browser = await p.chromium.launch(headless=True)
            print("  ✓ Browser launched successfully")
            
            # Test 3: Try to create a page
            print("\n⏳ Test 3: Creating a new page...")
            page = await browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            print("  ✓ Page created successfully")
            
            # Test 4: Try to navigate to a simple website
            print("\n⏳ Test 4: Navigating to example.com...")
            await page.goto('https://example.com', wait_until='networkidle', timeout=30000)
            print("  ✓ Navigation successful")
            
            # Test 5: Try to get page content
            print("\n⏳ Test 5: Retrieving page content...")
            html_content = await page.content()
            print(f"  ✓ Retrieved {len(html_content)} characters of HTML")
            print(f"  - First 200 chars: {html_content[:200]}")
            
            # Test 6: Try Harvard URL
            print("\n⏳ Test 6: Testing Harvard news site...")
            await page.goto('https://news.harvard.edu/gazette/', wait_until='networkidle', timeout=30000)
            harvard_html = await page.content()
            print(f"  ✓ Retrieved {len(harvard_html)} characters from Harvard")
            
            await browser.close()
            print("\n✓ Browser closed successfully")
            
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Playwright is working correctly!")
        print("=" * 80)
        
    except PlaywrightTimeoutError as e:
        print(f"\n❌ TIMEOUT ERROR: {e}")
        print("\nPossible causes:")
        print("  - Slow internet connection")
        print("  - Website is blocking automated access")
        print("  - Firewall/proxy blocking the request")
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}")
        
        if "Executable doesn't exist" in error_msg or "browser executable" in error_msg.lower():
            print("\n⚠️  PLAYWRIGHT BROWSERS NOT INSTALLED")
            print("\nTo fix this, run:")
            print("  playwright install chromium")
        else:
            print("\nUnexpected error occurred. Full error:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright())
