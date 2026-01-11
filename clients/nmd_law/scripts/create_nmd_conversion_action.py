"""
Create Offline Conversion Action for NMD Law Group
===================================================

Creates two conversion actions:
1. "Lead Form Submission" - Primary conversion for form fills
2. "Qualified Lead" - Offline conversion for leads marked qualified in CRM

Run once to set up the conversion actions.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv

load_dotenv()

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# NMD Law Group Configuration
NMD_CUSTOMER_ID = "7562650658"


def create_conversion_action(
    client,
    customer_id: str,
    name: str,
    category: str,
    conversion_type: str = "UPLOAD_CLICKS",
    default_value: float = 0,
    currency: str = "DKK",
    dry_run: bool = True,
):
    """Create a conversion action."""
    conversion_action_service = client.get_service("ConversionActionService")

    conversion_action_operation = client.get_type("ConversionActionOperation")
    conversion_action = conversion_action_operation.create

    conversion_action.name = name

    # Set type
    if conversion_type == "UPLOAD_CLICKS":
        conversion_action.type_ = client.enums.ConversionActionTypeEnum.UPLOAD_CLICKS
    elif conversion_type == "WEBPAGE":
        conversion_action.type_ = client.enums.ConversionActionTypeEnum.WEBPAGE

    # Set category
    category_map = {
        "LEAD": client.enums.ConversionActionCategoryEnum.SUBMIT_LEAD_FORM,
        "QUALIFIED_LEAD": client.enums.ConversionActionCategoryEnum.QUALIFIED_LEAD,
        "PURCHASE": client.enums.ConversionActionCategoryEnum.PURCHASE,
        "CONTACT": client.enums.ConversionActionCategoryEnum.CONTACT,
    }
    conversion_action.category = category_map.get(
        category, client.enums.ConversionActionCategoryEnum.DEFAULT
    )

    conversion_action.status = client.enums.ConversionActionStatusEnum.ENABLED

    # Value settings
    conversion_action.value_settings.default_value = default_value
    conversion_action.value_settings.always_use_default_value = False
    conversion_action.value_settings.default_currency_code = currency

    # Attribution settings - data-driven if available, otherwise last click
    conversion_action.attribution_model_settings.attribution_model = (
        client.enums.AttributionModelEnum.GOOGLE_ADS_LAST_CLICK
    )

    # 90-day lookback window
    conversion_action.click_through_lookback_window_days = 90

    print(f"\n=== Creating Conversion Action ===")
    print(f"Name: {name}")
    print(f"Type: {conversion_type}")
    print(f"Category: {category}")

    if dry_run:
        print(f"[DRY RUN] Would create conversion action.")
        return None

    try:
        response = conversion_action_service.mutate_conversion_actions(
            customer_id=customer_id, operations=[conversion_action_operation]
        )

        resource_name = response.results[0].resource_name
        conversion_action_id = resource_name.split("/")[-1]

        print(f"✅ Created: {name}")
        print(f"   ID: {conversion_action_id}")
        return conversion_action_id

    except GoogleAdsException as ex:
        print(f"Error: {ex}")
        for error in ex.failure.errors:
            print(f"  - {error.message}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Create conversion actions for NMD Law Group"
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate only")
    args = parser.parse_args()

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip(),
        "use_proto_plus": True,
    }

    client = GoogleAdsClient.load_from_dict(config)

    print(f"Creating conversion actions for NMD Law Group (ID: {NMD_CUSTOMER_ID})")
    print("=" * 60)

    # 1. Create "Lead Form Submission" - for real-time form tracking
    lead_form_id = create_conversion_action(
        client=client,
        customer_id=NMD_CUSTOMER_ID,
        name="Lead Form Submission",
        category="LEAD",
        conversion_type="UPLOAD_CLICKS",  # We'll upload via API with GCLID
        default_value=500,  # Default lead value in DKK
        dry_run=args.dry_run,
    )

    # 2. Create "Qualified Lead" - for offline/CRM conversions
    qualified_lead_id = create_conversion_action(
        client=client,
        customer_id=NMD_CUSTOMER_ID,
        name="Qualified Lead (Offline)",
        category="QUALIFIED_LEAD",
        conversion_type="UPLOAD_CLICKS",
        default_value=2000,  # Higher value for qualified leads
        dry_run=args.dry_run,
    )

    # 3. Create "Phone Call Click" - for tracking tel: link clicks
    phone_click_id = create_conversion_action(
        client=client,
        customer_id=NMD_CUSTOMER_ID,
        name="Phone Call Click",
        category="CONTACT",
        conversion_type="UPLOAD_CLICKS",
        default_value=300,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 60)
    print("SUMMARY - Save these IDs for your n8n workflow:")
    print("=" * 60)
    print(f"NMD_CUSTOMER_ID = '{NMD_CUSTOMER_ID}'")
    if lead_form_id:
        print(f"LEAD_FORM_CONVERSION_ID = '{lead_form_id}'")
    if qualified_lead_id:
        print(f"QUALIFIED_LEAD_CONVERSION_ID = '{qualified_lead_id}'")
    if phone_click_id:
        print(f"PHONE_CLICK_CONVERSION_ID = '{phone_click_id}'")


if __name__ == "__main__":
    main()
