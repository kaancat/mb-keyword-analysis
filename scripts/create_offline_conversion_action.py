"""
Create Offline Conversion Action for Google Ads
================================================

This creates a conversion action that accepts Enhanced Conversions for Leads
(hashed email/phone matching, no gclid needed).

Run once per account.
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv(Path.home() / ".mondaybrew" / ".env")

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def create_offline_conversion_action(customer_id: str, dry_run: bool = True):
    """Create an offline conversion action with Enhanced Conversions enabled."""

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip(),
        "use_proto_plus": True,
    }

    client = GoogleAdsClient.load_from_dict(config)
    conversion_action_service = client.get_service("ConversionActionService")

    # Create the conversion action
    conversion_action_operation = client.get_type("ConversionActionOperation")
    conversion_action = conversion_action_operation.create

    conversion_action.name = "Offline Purchase (Enhanced)"
    conversion_action.type_ = client.enums.ConversionActionTypeEnum.UPLOAD_CLICKS
    conversion_action.category = client.enums.ConversionActionCategoryEnum.PURCHASE
    conversion_action.status = client.enums.ConversionActionStatusEnum.ENABLED

    # Value settings
    conversion_action.value_settings.default_value = 0
    conversion_action.value_settings.always_use_default_value = False
    conversion_action.value_settings.default_currency_code = "DKK"

    # Attribution settings
    conversion_action.attribution_model_settings.attribution_model = (
        client.enums.AttributionModelEnum.GOOGLE_ADS_LAST_CLICK
    )
    conversion_action.attribution_model_settings.data_driven_model_status = (
        client.enums.DataDrivenModelStatusEnum.UNSPECIFIED
    )

    # Click-through conversion window (90 days max)
    conversion_action.click_through_lookback_window_days = 90

    print(f"=== Creating Conversion Action ===")
    print(f"Customer ID: {customer_id}")
    print(f"Name: {conversion_action.name}")
    print(f"Type: UPLOAD_CLICKS (for offline conversions)")
    print(f"Category: PURCHASE")

    if dry_run:
        print(f"\n[DRY RUN] Would create conversion action.")
        print("Run without --dry-run to actually create it.")
        return

    try:
        response = conversion_action_service.mutate_conversion_actions(
            customer_id=customer_id, operations=[conversion_action_operation]
        )

        resource_name = response.results[0].resource_name
        # Extract ID from resource name: customers/123/conversionActions/456
        conversion_action_id = resource_name.split("/")[-1]

        print(f"\n✅ Created conversion action!")
        print(f"Resource name: {resource_name}")
        print(f"Conversion Action ID: {conversion_action_id}")
        print(f"\n👉 Update upload_offline_conversions.py with this ID:")
        print(f'   GOOGLE_ADS_CONVERSION_ACTION_ID = "{conversion_action_id}"')

    except GoogleAdsException as ex:
        print(f"Error: {ex}")
        for error in ex.failure.errors:
            print(f"  - {error.message}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--customer-id", default="5207009970", help="Google Ads customer ID"
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate only")
    args = parser.parse_args()

    create_offline_conversion_action(args.customer_id, args.dry_run)
