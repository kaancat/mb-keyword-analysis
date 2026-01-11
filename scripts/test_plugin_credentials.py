#!/usr/bin/env python3
"""
Test that credentials and API access work from any directory.

This script verifies that the plugin's sys.path fixes work correctly,
meaning it can be called from anywhere and still find its modules.

Usage:
    # From plugin directory
    cd ~/Desktop/Plugins/mb-keyword-analysis
    python scripts/test_plugin_credentials.py

    # From ANY other directory (this is the important test)
    cd ~/Desktop/Projects/some-other-project
    python ~/.claude/plugins/cache/mb-plugins/mb-keyword-analysis/1.3.0/scripts/test_plugin_credentials.py
"""

import sys
from pathlib import Path

# Add plugin root to path (same pattern as all services)
_plugin_root = Path(__file__).parent.parent
if str(_plugin_root) not in sys.path:
    sys.path.insert(0, str(_plugin_root))

print("=" * 60)
print("MB-KEYWORD-ANALYSIS PLUGIN VERIFICATION")
print("=" * 60)
print(f"Script location: {__file__}")
print(f"Plugin root: {_plugin_root}")
print(f"Current working directory: {Path.cwd()}")
print()

# Test 1: Credentials loading
print("1. Testing credentials loading...")
try:
    from backend.services.credentials import ensure_credentials

    source = ensure_credentials()
    print(f"   ✓ Loaded credentials from: {source}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Keyword Planner API
print("\n2. Testing Keyword Planner API connection...")
try:
    from backend.services.keyword_planner import KeywordPlannerService

    kp = KeywordPlannerService()
    print("   ✓ KeywordPlannerService initialized successfully")
except Exception as e:
    print(f"   ✗ FAILED to initialize KeywordPlannerService: {e}")
    sys.exit(1)

# Test 3: Make an actual API call
print("\n3. Testing actual API call (keyword: 'test')...")
try:
    results = kp.generate_keyword_ideas(
        keywords=["test"],
        location_ids=["2840"],  # USA (reliable test location)
        language_id="1000",  # English
    )

    if not results:
        print("   ✗ FAILED: API returned no results")
        sys.exit(1)

    # Verify data has source marker (proves it's real, not hallucinated)
    if "_source" not in results[0]:
        print("   ✗ FAILED: Results missing _source marker")
        sys.exit(1)

    if results[0]["_source"] != "google_ads_api":
        print(f"   ✗ FAILED: Unexpected source: {results[0]['_source']}")
        sys.exit(1)

    print(f"   ✓ Got {len(results)} keyword ideas from Google Ads API")
    print(
        f"   Sample: '{results[0]['text']}' - {results[0]['avg_monthly_searches']} monthly searches"
    )

except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Plugin is working correctly!")
print("=" * 60)
print("\nThis means:")
print("  - Credentials load from ~/.mondaybrew/.env")
print("  - Python imports work from any directory")
print("  - Google Ads API returns real data (not hallucinated)")
print("  - The _source marker proves data authenticity")
