import os
import sys
import time
import base64
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.services.ads_connector import AdsConnector

def test_write_operations():
    # Load .env from project root
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    print(f"Loading .env from: {os.path.abspath(env_path)}")
    load_dotenv(dotenv_path=env_path)
    
    # Override Login Customer ID for Test Account
    os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = "3135586021"
    print("Overriding GOOGLE_ADS_LOGIN_CUSTOMER_ID to 3135586021 for test account access.")
    
    # Initialize connector
    try:
        connector = AdsConnector()
    except Exception as e:
        print(f"Error initializing AdsConnector: {e}")
        return
    
    # Get Customer ID (Test Account)
    # Created via create_test_account.py
    customer_id = "5912422766"
    print(f"Using Customer ID: {customer_id}")

    print(f"Testing Write Operations for Customer ID: {customer_id} (LIVE TEST on Test Account)")
    print("-" * 50)

    created_resources = []

    try:
        # [1] Creating Campaign Budget (Real)
        print("\n[1] Creating Campaign Budget (Real)...")
        budget_res = connector.create_campaign_budget(
            customer_id=customer_id,
            amount_micros=5000000,
            name=f"Test Budget {int(time.time())}",
            validate_only=False
        )
        print(f"Created campaign budget: {budget_res.get('resource')}")
        print(f"Result: {budget_res}")

        if not budget_res.get('success'):
            print("Failed to create budget. Aborting.")
            return

        budget_resource = budget_res.get('resource')

        # [2] Creating Campaign (Real) - Testing Smart Bidding (Manual CPC for now due to no conversions)
        print("\n[2] Creating Campaign (Real) with Manual CPC (Smart Bidding param check)...")
        camp_res = connector.create_campaign(
            customer_id=customer_id,
            budget_resource=budget_resource,
            name=f"Test Campaign {int(time.time())}",
            advertising_channel_type="SEARCH",
            status="PAUSED",
            bidding_strategy_type="MANUAL_CPC",
            # target_cpa_micros=10000000, # Not used for Manual CPC
            validate_only=False
        )
        print(f"Created campaign: {camp_res.get('resource')}")
        print(f"Result: {camp_res}")

        if not camp_res.get('success'):
            print("Failed to create campaign. Aborting.")
            return

        campaign_resource = camp_res.get('resource')
        campaign_id = campaign_resource.split('/')[-1]

        # [3] Creating Ad Group (Real)
        print("\n[3] Creating Ad Group (Real)...")
        ad_group_res = connector.create_ad_group(
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=f"Test Ad Group {int(time.time())}",
            cpc_bid_micros=1000000,
            validate_only=False
        )
        print(f"Created ad group: {ad_group_res.get('resource')}")
        print(f"Result: {ad_group_res}")

        if not ad_group_res.get('success'):
            print("Failed to create ad group. Aborting.")
            # Try to clean up campaign
            connector.remove_campaign(customer_id, campaign_id, validate_only=False)
            return

        ad_group_resource = ad_group_res.get('resource')
        ad_group_id = ad_group_resource.split('/')[-1]

        # [4] Adding Keywords (Real)
        print("\n[4] Adding Keywords (Real)...")
        kw_res = connector.add_keywords(
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=["test keyword 1", "test keyword 2"],
            validate_only=False
        )
        print(f"Added {len(kw_res.get('resources', []))} keywords to ad group {ad_group_id}")
        print(f"Result: {kw_res}")

        # [5] Creating RSA (Real) with Pinning
        print("\n[5] Creating RSA (Real) with Pinning...")
        rsa_res = connector.create_responsive_search_ad(
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=[
                {'text': "Pinned Headline 1", 'pinned_field': "HEADLINE_1"},
                "Unpinned Headline 2",
                "Unpinned Headline 3"
            ],
            descriptions=[
                {'text': "Pinned Description 1", 'pinned_field': "DESCRIPTION_1"},
                "Unpinned Description 2"
            ],
            final_urls=["https://www.example.com"],
            validate_only=False
        )
        print(f"Created RSA: {rsa_res.get('resource')}")
        print(f"Result: {rsa_res}")

        # [6] Creating Label (Real)
        print("\n[6] Creating Label (Real)...")
        label_res = connector.create_label(
            customer_id=customer_id,
            name=f"Test Label {int(time.time())}",
            validate_only=False
        )
        print(f"Created label: {label_res.get('resource')}")
        
        if label_res.get('success'):
            label_resource = label_res.get('resource')
            # Apply Label to Campaign
            print("\n[6b] Applying Label to Campaign...")
            apply_res = connector.apply_label(
                customer_id=customer_id,
                resource_name=campaign_resource,
                label_resource_name=label_resource,
                validate_only=False
            )
            print(f"Applied label result: {apply_res}")

        # [7] Creating Callout Assets (Real)
        print("\n[7] Creating Callout Assets (Real)...")
        callout_res = connector.create_callout_assets(
            customer_id=customer_id,
            callout_texts=["Free Shipping", "24/7 Support"],
            campaign_id=campaign_id,
            validate_only=False
        )
        print(f"Created callouts result: {callout_res}")

    finally:
        # [8] Cleanup
        print("\n[Cleanup] Removing Test Campaign...")
        try:
            remove_res = connector.remove_campaign(
                customer_id=customer_id,
                campaign_id=campaign_id,
                validate_only=False
            )
            print(f"Removal result for campaign {campaign_id}: {remove_res}")
        except Exception as e:
            print(f"Error cleaning up campaign: {e}")

    print("Test Complete.")

if __name__ == "__main__":
    test_write_operations()
