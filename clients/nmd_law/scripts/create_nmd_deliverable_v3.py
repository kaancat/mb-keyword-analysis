#!/usr/bin/env python3
"""Create NMD Law Group Google Ads deliverable v3 - Danish only, proper ROI tab."""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from scripts.add_roi_tab import add_roi_tab_v2


def main():
    # Check env vars
    refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

    if not all([refresh_token, client_id, client_secret]):
        print("ERROR: Missing credentials")
        return

    print("Credentials loaded successfully")

    # Initialize credentials
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    service = build("sheets", "v4", credentials=creds)

    # Load data files (Danish only)
    with open("/tmp/nmd_tab1_reclassified.json", "r", encoding="utf-8") as f:
        danish_keywords = json.load(f)

    with open("/tmp/nmd_competitor_keywords.json", "r", encoding="utf-8") as f:
        competitor_keywords = json.load(f)

    with open("/tmp/nmd_tab2_restructured.json", "r", encoding="utf-8") as f:
        campaign_structure = json.load(f)

    with open("/tmp/nmd_tab3_restructured.json", "r", encoding="utf-8") as f:
        ads = json.load(f)

    # Filter to Danish-only campaigns
    danish_campaigns = [
        row for row in campaign_structure if "EN | Search" not in row["Campaign"]
    ]

    danish_ads = [ad for ad in ads if "EN | Search" not in ad["Campaign"]]

    # Create spreadsheet with 4 sheets (ROI tab will be added separately)
    print("Creating spreadsheet...")
    spreadsheet_body = {
        "properties": {
            "title": "[KEYWORD ANALYSIS & AD COPY] - NMD Law Group - Udlændingeret v3"
        },
        "sheets": [
            {"properties": {"title": "Keyword Analysis"}},
            {"properties": {"title": "Competitor Keywords"}},
            {"properties": {"title": "Campaign Structure"}},
            {"properties": {"title": "Ad Copy"}},
        ],
    }

    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet_body, fields="spreadsheetId,spreadsheetUrl")
        .execute()
    )
    spreadsheet_id = spreadsheet.get("spreadsheetId")
    spreadsheet_url = spreadsheet.get("spreadsheetUrl")
    print(f"Created spreadsheet: {spreadsheet_url}")

    # ============ TAB 1: Keyword Analysis ============
    print("\nWriting Tab 1: Keyword Analysis...")
    tab1_headers = [
        "Keyword",
        "Avg. Monthly Searches",
        "YoY Change",
        "Competition",
        "Top of page bid (low range)",
        "Top of page bid (high range)",
        "Category",
        "Intent",
        "Include",
    ]
    tab1_rows = [tab1_headers]

    # Sort by intent (High first) then by volume
    sorted_keywords = sorted(
        danish_keywords,
        key=lambda x: (
            0 if x["Intent"] == "High" else (1 if x["Intent"] == "Medium" else 2),
            -x["Avg. Monthly Searches"],
        ),
    )

    for kw in sorted_keywords:
        tab1_rows.append(
            [
                kw["Keyword"],
                kw["Avg. Monthly Searches"],
                kw["YoY Change"],
                kw["Competition"],
                kw["Top of page bid (low range)"],
                kw["Top of page bid (high range)"],
                kw["Category"],
                kw["Intent"],
                "TRUE" if kw.get("Include", True) else "FALSE",
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Keyword Analysis'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab1_rows},
    ).execute()
    print(f"  Written {len(tab1_rows)-1} keywords (sorted by intent)")

    # ============ TAB 2: Competitor Keywords ============
    print("\nWriting Tab 2: Competitor Keywords...")
    tab2_headers = [
        "Keyword",
        "Competitor",
        "Est. Monthly Searches",
        "Competition",
        "Match Type",
        "Intent",
        "Notes",
    ]
    tab2_rows = [tab2_headers]
    for kw in competitor_keywords:
        notes = ""
        if "globe" in kw["Keyword"].lower():
            notes = "Largest competitor brand volume"
        elif "homann" in kw["Keyword"].lower():
            notes = "Strong CPH presence"
        elif (
            "immlaw" in kw["Keyword"].lower()
            or "immigrationlaw" in kw["Keyword"].lower()
        ):
            notes = "First specialist firm in DK"

        tab2_rows.append(
            [
                kw["Keyword"],
                kw["Competitor"],
                kw["Avg. Monthly Searches"],
                kw["Competition"],
                kw["Match Type"],
                kw["Intent"],
                notes,
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Competitor Keywords'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab2_rows},
    ).execute()
    print(f"  Written {len(tab2_rows)-1} competitor keywords")

    # ============ TAB 3: Campaign Structure ============
    print("\nWriting Tab 3: Campaign Structure...")
    tab3_headers = [
        "Campaign",
        "Ad Group",
        "Keyword",
        "Match Type",
        "Final URL",
        "Intent",
    ]
    tab3_rows = [tab3_headers]

    # Sort by campaign priority (High Intent first)
    campaign_priority = {
        "mb | DA | Search | Udlændingeret - High Intent": 0,
        "mb | DA | Search | Udlændingeret - Mid Funnel": 1,
        "mb | DA | Search | Udlændingeret - Discovery": 2,
        "mb | DA | Search | Competitor": 3,
    }

    sorted_structure = sorted(
        danish_campaigns, key=lambda x: campaign_priority.get(x["Campaign"], 99)
    )

    for row in sorted_structure:
        tab3_rows.append(
            [
                row["Campaign"],
                row["Ad Group"],
                row["Keyword"],
                row["Match Type"],
                row["Final URL"],
                row["Intent"],
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Campaign Structure'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab3_rows},
    ).execute()
    print(f"  Written {len(tab3_rows)-1} keyword assignments")

    # ============ TAB 4: Ad Copy ============
    print("\nWriting Tab 4: Ad Copy...")
    tab4_headers = [
        "Campaign",
        "Ad Group",
        "Headline 1",
        "Headline 1 position",
        "Headline 2",
        "Headline 2 position",
        "Headline 3",
        "Headline 3 position",
        "Headline 4",
        "Headline 4 position",
        "Headline 5",
        "Headline 5 position",
        "Headline 6",
        "Headline 6 position",
        "Headline 7",
        "Headline 7 position",
        "Headline 8",
        "Headline 8 position",
        "Headline 9",
        "Headline 9 position",
        "Headline 10",
        "Headline 10 position",
        "Description 1",
        "Description 1 position",
        "Description 2",
        "Description 2 position",
        "Description 3",
        "Description 3 position",
        "Description 4",
        "Description 4 position",
        "Path 1",
        "Path 2",
        "Final URL",
    ]
    tab4_rows = [tab4_headers]
    for ad in danish_ads:
        row = [
            ad["Campaign"],
            ad["Ad Group"],
            ad["Headline 1"],
            ad.get("Headline 1 position", ""),
            ad["Headline 2"],
            ad.get("Headline 2 position", ""),
            ad.get("Headline 3", ""),
            ad.get("Headline 3 position", ""),
            ad.get("Headline 4", ""),
            ad.get("Headline 4 position", ""),
            ad.get("Headline 5", ""),
            ad.get("Headline 5 position", ""),
            ad.get("Headline 6", ""),
            ad.get("Headline 6 position", ""),
            ad.get("Headline 7", ""),
            ad.get("Headline 7 position", ""),
            ad.get("Headline 8", ""),
            ad.get("Headline 8 position", ""),
            ad.get("Headline 9", ""),
            ad.get("Headline 9 position", ""),
            ad.get("Headline 10", ""),
            ad.get("Headline 10 position", ""),
            ad["Description 1"],
            ad.get("Description 1 position", ""),
            ad["Description 2"],
            ad.get("Description 2 position", ""),
            ad.get("Description 3", ""),
            ad.get("Description 3 position", ""),
            ad.get("Description 4", ""),
            ad.get("Description 4 position", ""),
            ad["Path 1"],
            ad["Path 2"],
            ad["Final URL"],
        ]
        tab4_rows.append(row)

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Ad Copy'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab4_rows},
    ).execute()
    print(f"  Written {len(tab4_rows)-1} RSA ads")

    # ============ TAB 5: ROI Beregner (using proper script) ============
    print("\nAdding Tab 5: ROI Beregner...")

    # For law firm: higher CPC (20-40 DKK typical), higher profit per customer
    add_roi_tab_v2(
        spreadsheet_id=spreadsheet_id,
        client_name="NMD Law Group",
        budget=5000,  # Reasonable starting budget for law firm
        profit_per_customer=5000,  # Typical immigration case fee
        cpc=25,  # Higher CPC for legal keywords
    )

    # Calculate totals
    total_volume = sum(k["Avg. Monthly Searches"] for k in danish_keywords)
    high_intent_count = len([k for k in danish_keywords if k["Intent"] == "High"])
    med_intent_count = len([k for k in danish_keywords if k["Intent"] == "Medium"])
    low_intent_count = len([k for k in danish_keywords if k["Intent"] == "Low"])

    print("\n" + "=" * 60)
    print("NMD LAW GROUP DELIVERABLE v3 COMPLETE!")
    print("=" * 60)
    print(f"\nSpreadsheet URL: {spreadsheet_url}")
    print(f"Spreadsheet ID: {spreadsheet_id}")

    print("\n📊 KEYWORD SUMMARY")
    print("-" * 40)
    print(f"  Total keywords: {len(danish_keywords)}")
    print(f"  Total monthly searches: {total_volume:,}")
    print(
        f"  High Intent (transactional): {high_intent_count} ({high_intent_count/len(danish_keywords)*100:.1f}%)"
    )
    print(
        f"  Medium Intent (commercial): {med_intent_count} ({med_intent_count/len(danish_keywords)*100:.1f}%)"
    )
    print(
        f"  Low Intent (informational): {low_intent_count} ({low_intent_count/len(danish_keywords)*100:.1f}%)"
    )

    print("\n📈 CAMPAIGN STRUCTURE")
    print("-" * 40)
    campaigns = {}
    for row in danish_campaigns:
        camp = row["Campaign"]
        if camp not in campaigns:
            campaigns[camp] = 0
        campaigns[camp] += 1

    for camp, count in sorted(
        campaigns.items(), key=lambda x: campaign_priority.get(x[0], 99)
    ):
        print(f"  {camp}: {count} keywords")

    print("\n🎯 COMPETITOR TARGETING")
    print("-" * 40)
    competitors = set(kw["Competitor"] for kw in competitor_keywords)
    for comp in sorted(competitors):
        count = len([k for k in competitor_keywords if k["Competitor"] == comp])
        print(f"  {comp}: {count} keywords")

    print("\n✅ AD COPY")
    print("-" * 40)
    print(f"  Total RSA ads: {len(danish_ads)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
