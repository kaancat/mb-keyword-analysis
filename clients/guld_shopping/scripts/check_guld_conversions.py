#!/usr/bin/env python3
"""
Check conversion actions for Guld Design account
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from backend.services.ads_connector import AdsConnector


def main():
    customer_id = "1600121107"  # Guilddesign

    print(f"Checking conversion actions for customer: {customer_id}")
    print("=" * 70)

    ads = AdsConnector()

    # Get conversion actions
    conversions = ads.get_conversion_actions(customer_id)

    print(f"\nFound {len(conversions)} conversion actions:\n")

    for c in conversions:
        print(f"Name: {c.get('name', 'N/A')}")
        print(f"  ID: {c.get('id', 'N/A')}")
        print(f"  Type: {c.get('type', 'N/A')}")
        print(f"  Category: {c.get('category', 'N/A')}")
        print(f"  Status: {c.get('status', 'N/A')}")
        print(f"  Primary: {c.get('primary_for_goal', 'N/A')}")
        print(f"  Tag Tracking Status: {c.get('tag_tracking_status', 'N/A')}")
        print(f"  Attribution Model: {c.get('attribution_model', 'N/A')}")
        print("-" * 50)


if __name__ == "__main__":
    main()
