"""
Offline Conversions Upload Script for Karim Design
===================================================

This script takes Airtable export data and uploads offline conversions to:
1. Google Ads (via Enhanced Conversions for Leads - uses hashed email/phone)
2. Facebook (via Offline Conversions API - uses hashed email/phone)

No gclid/fbclid needed - the platforms match based on hashed PII.

Usage:
    python scripts/upload_offline_conversions.py --csv /path/to/airtable_export.csv --days 30
    python scripts/upload_offline_conversions.py --csv /path/to/airtable_export.csv --days 30 --dry-run
"""

import sys
import os
import argparse
import hashlib
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()


def hash_sha256(value: str) -> str:
    """Hash a value using SHA256 (required format for Google/Facebook)."""
    if not value:
        return ""
    # Normalize: lowercase, strip whitespace
    normalized = value.lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format for Denmark."""
    if not phone:
        return ""
    # Remove all non-digits
    digits = "".join(c for c in phone if c.isdigit())
    # Danish numbers: if 8 digits, add +45
    if len(digits) == 8:
        return f"+45{digits}"
    # If already has country code
    if len(digits) == 10 and digits.startswith("45"):
        return f"+{digits}"
    if len(digits) > 8:
        return f"+{digits}"
    return digits


def parse_airtable_csv(csv_path: str, days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Parse Airtable CSV export and extract conversion data.

    Returns list of conversions with:
    - email (raw)
    - phone (raw)
    - name (raw)
    - conversion_time (datetime)
    - conversion_value (float)
    """
    conversions = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Parse submission date
            submission_date_str = row.get("Submission Date", "")
            if not submission_date_str:
                continue

            try:
                # Format: "Nov 18, 2025"
                submission_date = datetime.strptime(submission_date_str, "%b %d, %Y")
            except ValueError:
                try:
                    # Try alternative format
                    submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
                except ValueError:
                    continue

            # Skip if older than cutoff
            if submission_date < cutoff_date:
                continue

            # Extract fields
            email = row.get("E-mail", "").strip()
            phone = row.get("Phone Number", "").strip()
            name = row.get("Name", "").strip()

            # Parse price - handle Danish format
            price_str = row.get("Price/Pris", "0")
            try:
                # Remove currency symbols, spaces, and handle comma as decimal
                price_clean = (
                    price_str.replace("DKK", "")
                    .replace("kr", "")
                    .replace(" ", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
                price = float(price_clean) if price_clean else 0
            except ValueError:
                price = 0

            # Skip if no email (required for matching)
            if not email:
                continue

            conversions.append(
                {
                    "email": email,
                    "phone": phone,
                    "name": name,
                    "conversion_time": submission_date,
                    "conversion_value": price,
                    "order_number": row.get("Order Number", ""),
                }
            )

    return conversions


# ============================================
# GOOGLE ADS - Enhanced Conversions for Leads
# ============================================


def upload_to_google_ads(
    conversions: List[Dict],
    customer_id: str,
    conversion_action_id: str,
    dry_run: bool = True,
):
    """
    Upload conversions to Google Ads using Enhanced Conversions for Leads.

    This uses hashed email/phone instead of gclid.
    """
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip(),
        "use_proto_plus": True,
    }

    client = GoogleAdsClient.load_from_dict(config)
    conversion_upload_service = client.get_service("ConversionUploadService")
    conversion_action_service = client.get_service("ConversionActionService")

    # Build conversion action resource name
    conversion_action_resource = (
        f"customers/{customer_id}/conversionActions/{conversion_action_id}"
    )

    # Build the conversions
    enhanced_conversions = []

    for conv in conversions:
        click_conversion = client.get_type("ClickConversion")

        # Set conversion action
        click_conversion.conversion_action = conversion_action_resource

        # Set conversion time (format: yyyy-mm-dd hh:mm:ss+|-hh:mm)
        conv_time = conv["conversion_time"].strftime("%Y-%m-%d %H:%M:%S+01:00")
        click_conversion.conversion_date_time = conv_time

        # Set value
        if conv["conversion_value"] > 0:
            click_conversion.conversion_value = float(conv["conversion_value"])
            click_conversion.currency_code = "DKK"

        # Set user identifiers (hashed)
        user_identifiers = []

        # Hashed email
        if conv["email"]:
            user_id = client.get_type("UserIdentifier")
            user_id.hashed_email = hash_sha256(conv["email"])
            user_identifiers.append(user_id)

        # Hashed phone
        if conv["phone"]:
            user_id = client.get_type("UserIdentifier")
            normalized_phone = normalize_phone(conv["phone"])
            user_id.hashed_phone_number = hash_sha256(normalized_phone)
            user_identifiers.append(user_id)

        click_conversion.user_identifiers.extend(user_identifiers)
        enhanced_conversions.append(click_conversion)

    if not enhanced_conversions:
        print("No conversions to upload to Google Ads.")
        return

    print(f"\n=== GOOGLE ADS UPLOAD ===")
    print(f"Customer ID: {customer_id}")
    print(f"Conversion Action: {conversion_action_resource}")
    print(f"Conversions to upload: {len(enhanced_conversions)}")

    if dry_run:
        print("\n[DRY RUN] Would upload the following conversions:")
        for i, conv in enumerate(conversions[:5]):
            print(
                f"  {i+1}. {conv['email']} | {conv['conversion_time'].strftime('%Y-%m-%d')} | {conv['conversion_value']} DKK"
            )
        if len(conversions) > 5:
            print(f"  ... and {len(conversions) - 5} more")
        return

    try:
        request = client.get_type("UploadClickConversionsRequest")
        request.customer_id = customer_id
        request.conversions = enhanced_conversions
        request.partial_failure = True

        response = conversion_upload_service.upload_click_conversions(request=request)

        if response.partial_failure_error:
            print(f"Partial failures: {response.partial_failure_error.message}")

        print(
            f"Successfully uploaded {len(response.results)} conversions to Google Ads"
        )

    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")


# ============================================
# FACEBOOK - Offline Conversions API
# ============================================


def upload_to_facebook(
    conversions: List[Dict], pixel_id: str, access_token: str, dry_run: bool = True
):
    """
    Upload conversions to Facebook using the Conversions API (Offline Events).

    Uses hashed email/phone for matching.
    """
    import requests
    import json
    import time

    # Facebook Conversions API endpoint
    url = f"https://graph.facebook.com/v18.0/{pixel_id}/events"

    # Build events
    events = []

    for conv in conversions:
        event = {
            "event_name": "Purchase",  # Or "Lead" if you prefer
            "event_time": int(conv["conversion_time"].timestamp()),
            "action_source": "physical_store",  # For offline conversions
            "user_data": {},
        }

        # Add hashed email
        if conv["email"]:
            event["user_data"]["em"] = [hash_sha256(conv["email"])]

        # Add hashed phone
        if conv["phone"]:
            normalized_phone = normalize_phone(conv["phone"])
            event["user_data"]["ph"] = [hash_sha256(normalized_phone)]

        # Add country (Denmark)
        event["user_data"]["country"] = [hash_sha256("dk")]

        # Add custom data (value, currency)
        if conv["conversion_value"] > 0:
            event["custom_data"] = {
                "value": conv["conversion_value"],
                "currency": "DKK",
            }

        events.append(event)

    if not events:
        print("No conversions to upload to Facebook.")
        return

    print(f"\n=== FACEBOOK UPLOAD ===")
    print(f"Pixel ID: {pixel_id}")
    print(f"Events to upload: {len(events)}")

    if dry_run:
        print("\n[DRY RUN] Would upload the following events:")
        for i, conv in enumerate(conversions[:5]):
            print(
                f"  {i+1}. {conv['email']} | {conv['conversion_time'].strftime('%Y-%m-%d')} | {conv['conversion_value']} DKK"
            )
        if len(conversions) > 5:
            print(f"  ... and {len(conversions) - 5} more")
        return

    # Upload in batches of 1000 (Facebook limit)
    batch_size = 1000
    total_uploaded = 0

    for i in range(0, len(events), batch_size):
        batch = events[i : i + batch_size]

        payload = {
            "data": json.dumps(batch),
            "access_token": access_token,
        }

        try:
            response = requests.post(url, data=payload)
            result = response.json()

            if "error" in result:
                print(f"Facebook API error: {result['error']}")
            else:
                events_received = result.get("events_received", 0)
                total_uploaded += events_received
                print(f"Batch {i // batch_size + 1}: Uploaded {events_received} events")

        except Exception as e:
            print(f"Error uploading to Facebook: {e}")

        # Rate limiting
        time.sleep(1)

    print(f"\nTotal uploaded to Facebook: {total_uploaded} events")


# ============================================
# MAIN
# ============================================


def main():
    parser = argparse.ArgumentParser(
        description="Upload offline conversions to Google Ads and Facebook"
    )
    parser.add_argument("--csv", required=True, help="Path to Airtable CSV export")
    parser.add_argument(
        "--days", type=int, default=30, help="Only upload conversions from last N days"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without uploading"
    )
    parser.add_argument(
        "--google-only", action="store_true", help="Only upload to Google Ads"
    )
    parser.add_argument(
        "--facebook-only", action="store_true", help="Only upload to Facebook"
    )

    args = parser.parse_args()

    # Parse CSV
    print(f"Parsing CSV: {args.csv}")
    print(f"Looking for conversions from last {args.days} days...")

    conversions = parse_airtable_csv(args.csv, args.days)

    print(f"\nFound {len(conversions)} conversions")

    if not conversions:
        print("No conversions found. Exiting.")
        return

    # Show summary
    total_value = sum(c["conversion_value"] for c in conversions)
    print(f"Total value: {total_value:,.0f} DKK")
    print(
        f"Date range: {min(c['conversion_time'] for c in conversions).strftime('%Y-%m-%d')} to {max(c['conversion_time'] for c in conversions).strftime('%Y-%m-%d')}"
    )

    # Karim Design IDs
    GOOGLE_ADS_CUSTOMER_ID = "5207009970"
    GOOGLE_ADS_CONVERSION_ACTION_ID = "7399889482"  # Created 2025-11-28

    FACEBOOK_PIXEL_ID = "326076256074833"  # From Trafft
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")  # Need to set this

    # Upload to Google Ads
    if not args.facebook_only:
        if GOOGLE_ADS_CONVERSION_ACTION_ID == "YOUR_CONVERSION_ACTION_ID":
            print("\n⚠️  Google Ads: Need to create a conversion action first.")
            print("   Run: python scripts/create_google_ads_conversion_action.py")
        else:
            upload_to_google_ads(
                conversions=conversions,
                customer_id=GOOGLE_ADS_CUSTOMER_ID,
                conversion_action_id=GOOGLE_ADS_CONVERSION_ACTION_ID,
                dry_run=args.dry_run,
            )

    # Upload to Facebook
    if not args.google_only:
        if not FACEBOOK_ACCESS_TOKEN:
            print("\n⚠️  Facebook: Need to set FACEBOOK_ACCESS_TOKEN in .env")
            print("   Get it from: https://business.facebook.com/events_manager")
        else:
            upload_to_facebook(
                conversions=conversions,
                pixel_id=FACEBOOK_PIXEL_ID,
                access_token=FACEBOOK_ACCESS_TOKEN,
                dry_run=args.dry_run,
            )


if __name__ == "__main__":
    main()
