#!/usr/bin/env python3
"""
Add Negative Keywords to Karim Design Account (5207009970)

Based on audit analysis, this script adds:
1. Konkurrenter campaign: Block konfirmation searches (wrong product)
2. Radius campaign: Block geographic leakage (Jutland searches)
3. Account-level: Block low-intent/irrelevant searches

Usage:
    python scripts/add_negative_keywords.py
"""

import os
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(Path.home() / ".mondaybrew" / ".env")

from backend.services.ads_connector import AdsConnector


def main():
    print("=" * 60)
    print("KARIM DESIGN - NEGATIVE KEYWORD IMPLEMENTATION")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize connector
    ads = AdsConnector()

    # Account and Campaign IDs
    CUSTOMER_ID = "5207009970"
    CAMPAIGNS = {
        "brand": "17488875745",
        "radius": "17488948942",
        "konkurrenter": "22329468614",
        "kjoleproevning": "22333103497",
    }

    results = {"konkurrenter": None, "radius": None, "shared_list": None}

    # ============================================
    # 1. KONKURRENTER CAMPAIGN - Block Konfirmation
    # ============================================
    print("\n" + "-" * 40)
    print("1. Adding negatives to Konkurrenter campaign")
    print("   Blocking: konfirmation searches (wrong product)")
    print("-" * 40)

    konfirmation_negatives = [
        "konfirmation",
        "konfirmationskjoler",
        "konfirmations",
        "konfirmationskjole",
    ]

    print(f"   Keywords to add: {konfirmation_negatives}")

    try:
        results["konkurrenter"] = ads.add_campaign_negative_keywords(
            customer_id=CUSTOMER_ID,
            campaign_id=CAMPAIGNS["konkurrenter"],
            keywords=konfirmation_negatives,
        )
        print(
            f"   Result: {len(results['konkurrenter'].get('added', []))} keywords added"
        )
        if results["konkurrenter"].get("errors"):
            print(f"   Errors: {results['konkurrenter']['errors']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        results["konkurrenter"] = {"error": str(e)}

    # ============================================
    # 2. RADIUS CAMPAIGN - Block Geographic Leakage
    # ============================================
    print("\n" + "-" * 40)
    print("2. Adding negatives to Radius campaign")
    print("   Blocking: Jutland/outside Copenhagen searches")
    print("-" * 40)

    geographic_negatives = [
        "hjallerup",
        "jylland",
        "nordjylland",
        "midtjylland",
        "sønderjylland",
        "fyn",
        "odense",
        "aalborg",
        "aarhus",
        "århus",
    ]

    print(f"   Keywords to add: {geographic_negatives}")

    try:
        results["radius"] = ads.add_campaign_negative_keywords(
            customer_id=CUSTOMER_ID,
            campaign_id=CAMPAIGNS["radius"],
            keywords=geographic_negatives,
        )
        print(f"   Result: {len(results['radius'].get('added', []))} keywords added")
        if results["radius"].get("errors"):
            print(f"   Errors: {results['radius']['errors']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        results["radius"] = {"error": str(e)}

    # ============================================
    # 3. ACCOUNT-LEVEL - Shared Negative List
    # ============================================
    print("\n" + "-" * 40)
    print("3. Creating shared negative keyword list")
    print("   Blocking: low-intent/irrelevant searches")
    print("-" * 40)

    account_negatives = [
        "billig",
        "billige",
        "brugt",
        "brugte",
        "gratis",
        "asos",
        "h&m",
        "zalando",
        "leje",
        "udlejning",
    ]

    print(f"   Keywords to add: {account_negatives}")

    try:
        # Create shared list
        results["shared_list"] = ads.add_shared_negative_keyword_list(
            customer_id=CUSTOMER_ID,
            list_name="MB | Account Negatives | Low Intent",
            keywords=account_negatives,
        )
        print(
            f"   Result: {len(results['shared_list'].get('added', []))} keywords added to shared list"
        )

        # Attach to all campaigns
        if results["shared_list"].get("list_resource"):
            print("\n   Attaching shared list to all campaigns...")
            for campaign_name, campaign_id in CAMPAIGNS.items():
                attach_result = ads.attach_shared_set_to_campaign(
                    customer_id=CUSTOMER_ID,
                    campaign_id=campaign_id,
                    shared_set_resource=results["shared_list"]["list_resource"],
                )
                status = "OK" if attach_result.get("success") else "FAILED"
                print(f"   - {campaign_name}: {status}")

        if results["shared_list"].get("errors"):
            print(f"   Errors: {results['shared_list']['errors']}")

    except Exception as e:
        print(f"   ERROR: {e}")
        results["shared_list"] = {"error": str(e)}

    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_added = 0

    if results["konkurrenter"] and results["konkurrenter"].get("added"):
        count = len(results["konkurrenter"]["added"])
        total_added += count
        print(f"Konkurrenter: {count} negatives added")
    else:
        print(
            f"Konkurrenter: FAILED - {results.get('konkurrenter', {}).get('error', 'unknown error')}"
        )

    if results["radius"] and results["radius"].get("added"):
        count = len(results["radius"]["added"])
        total_added += count
        print(f"Radius: {count} negatives added")
    else:
        print(
            f"Radius: FAILED - {results.get('radius', {}).get('error', 'unknown error')}"
        )

    if results["shared_list"] and results["shared_list"].get("added"):
        count = len(results["shared_list"]["added"])
        total_added += count
        print(f"Shared List: {count} negatives added (applied to all campaigns)")
    else:
        print(
            f"Shared List: FAILED - {results.get('shared_list', {}).get('error', 'unknown error')}"
        )

    print(f"\nTOTAL: {total_added} negative keywords implemented")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
