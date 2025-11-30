"""
Test the shared tools directly to verify they work correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.tools import analyze_html_structure, test_selector

async def test_tools():
    """Test the analysis tools directly."""
    print("=" * 80)
    print("TESTING SHARED TOOLS")
    print("=" * 80)
    
    test_url = "https://news.harvard.edu/gazette/"
    
    # Test 1: analyze_html_structure
    print("\n⏳ Test 1: Running analyze_html_structure...")
    result1 = await analyze_html_structure(test_url)
    print(f"\nResult length: {len(result1)} characters")
    print(f"First 500 chars:\n{result1[:500]}")
    
    if "❌ Error" in result1:
        print("\n❌ ERROR DETECTED IN TOOL OUTPUT")
    else:
        print("\n✓ Tool executed successfully")
    
    # Test 2: test_selector
    print("\n" + "=" * 80)
    print("\n⏳ Test 2: Running test_selector...")
    result2 = await test_selector(test_url, "h1", "")
    print(f"\nResult length: {len(result2)} characters")
    print(f"First 500 chars:\n{result2[:500]}")
    
    if "❌ Error" in result2:
        print("\n❌ ERROR DETECTED IN TOOL OUTPUT")
    else:
        print("\n✓ Tool executed successfully")
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_tools())
