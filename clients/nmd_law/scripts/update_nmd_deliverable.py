#!/usr/bin/env python3
"""Update NMD Law Group Google Ads deliverable with enhanced analysis."""

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

    # Load all data files
    with open("/tmp/nmd_tab1_reclassified.json", "r", encoding="utf-8") as f:
        danish_keywords = json.load(f)

    with open("/tmp/nmd_english_keywords.json", "r", encoding="utf-8") as f:
        english_keywords = json.load(f)

    with open("/tmp/nmd_competitor_keywords.json", "r", encoding="utf-8") as f:
        competitor_keywords = json.load(f)

    with open("/tmp/nmd_tab2_restructured.json", "r", encoding="utf-8") as f:
        campaign_structure = json.load(f)

    with open("/tmp/nmd_tab3_restructured.json", "r", encoding="utf-8") as f:
        ads = json.load(f)

    # Create spreadsheet with 6 sheets
    print("Creating spreadsheet...")
    spreadsheet_body = {
        "properties": {
            "title": "[KEYWORD ANALYSIS & AD COPY] - NMD Law Group - Udlændingeret v2"
        },
        "sheets": [
            {"properties": {"title": "Keyword Analysis (DA)"}},
            {"properties": {"title": "Keyword Analysis (EN)"}},
            {"properties": {"title": "Competitor Keywords"}},
            {"properties": {"title": "Campaign Structure"}},
            {"properties": {"title": "Ad Copy"}},
            {"properties": {"title": "ROI Beregner"}},
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

    # ============ TAB 1: Danish Keyword Analysis ============
    print("\nWriting Tab 1: Danish Keyword Analysis...")
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
    for kw in danish_keywords:
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
        range="'Keyword Analysis (DA)'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab1_rows},
    ).execute()
    print(f"  Written {len(tab1_rows)-1} Danish keywords")

    # ============ TAB 2: English Keyword Analysis ============
    print("\nWriting Tab 2: English Keyword Analysis...")
    tab2_headers = [
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
    tab2_rows = [tab2_headers]
    for kw in english_keywords:
        tab2_rows.append(
            [
                kw["Keyword"],
                kw["Avg. Monthly Searches"],
                kw.get("YoY Change", ""),
                kw["Competition"],
                kw["Top of page bid (low range)"],
                kw["Top of page bid (high range)"],
                kw["Category"],
                kw["Intent"],
                "TRUE" if kw.get("Include", False) else "FALSE",
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Keyword Analysis (EN)'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab2_rows},
    ).execute()
    print(f"  Written {len(tab2_rows)-1} English keywords")

    # ============ TAB 3: Competitor Keywords ============
    print("\nWriting Tab 3: Competitor Keywords...")
    tab3_headers = [
        "Keyword",
        "Competitor",
        "Est. Monthly Searches",
        "Competition",
        "Match Type",
        "Intent",
    ]
    tab3_rows = [tab3_headers]
    for kw in competitor_keywords:
        tab3_rows.append(
            [
                kw["Keyword"],
                kw["Competitor"],
                kw["Avg. Monthly Searches"],
                kw["Competition"],
                kw["Match Type"],
                kw["Intent"],
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Competitor Keywords'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab3_rows},
    ).execute()
    print(f"  Written {len(tab3_rows)-1} competitor keywords")

    # ============ TAB 4: Campaign Structure ============
    print("\nWriting Tab 4: Campaign Structure...")
    tab4_headers = [
        "Campaign",
        "Ad Group",
        "Keyword",
        "Match Type",
        "Final URL",
        "Intent",
    ]
    tab4_rows = [tab4_headers]
    for row in campaign_structure:
        tab4_rows.append(
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
        body={"values": tab4_rows},
    ).execute()
    print(f"  Written {len(tab4_rows)-1} keyword assignments")

    # ============ TAB 5: Ad Copy ============
    print("\nWriting Tab 5: Ad Copy...")
    tab5_headers = [
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
    tab5_rows = [tab5_headers]
    for ad in ads:
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
        tab5_rows.append(row)

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Ad Copy'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab5_rows},
    ).execute()
    print(f"  Written {len(tab5_rows)-1} RSA ads")

    # ============ TAB 6: ROI Beregner ============
    print("\nWriting Tab 6: ROI Beregner...")

    roi_rows = [
        ["📊 DINE TAL", "", "Hvad betyder det?", ""],
        ["", "", "", ""],
        ["Månedligt annoncebudget", "", "", ""],
        ["Fortjeneste pr. kunde", "", "Hvad tjener I pr. kunde?", ""],
        ["Lukningsrate %", "15", "Leads der bliver til kunder", ""],
        ["", "", "", ""],
        ["📈 KAMPAGNE ESTIMATER", "", "Hvad betyder det?", ""],
        ["", "", "", ""],
        ["Pris pr. klik (CPC)", "25", "Typisk for advokat-branchen (høj)", ""],
        ["Website konverteringsrate %", "3", "Besøgende der udfylder formular", ""],
        ["", "", "", ""],
        ["🧮 BEREGNEDE RESULTATER", "", "Forklaring", "Beregning"],
        ["", "", "", ""],
        [
            "Estimerede klik/måned",
            '=IF(B3="", "-", ROUND(B3/IF(B9="",25,B9),0))',
            "Budget ÷ CPC",
            '=IF(B3="","-",B3&" kr ÷ "&IF(B9="",25,B9)&" kr = "&B14&" klik")',
        ],
        [
            "Estimerede leads/måned",
            '=IF(B3="", "-", ROUND(B14*(IF(B10="",3,B10)/100),1))',
            "Klik × konverteringsrate",
            '=IF(B3="","-",B14&" klik × "&IF(B10="",3,B10)&"% = "&B15&" leads")',
        ],
        [
            "Estimerede kunder/måned",
            '=IF(B3="", "-", ROUND(B15*(IF(B5="",15,B5)/100),1))',
            "Leads × lukningsrate",
            '=IF(B3="","-",B15&" leads × "&IF(B5="",15,B5)&"% = "&B16&" kunder")',
        ],
        [
            "Estimeret omsætning/måned",
            '=IF(OR(B3="",B4=""), "-", ROUND(B16*B4,0))',
            "Kunder × fortjeneste",
            '=IF(OR(B3="",B4=""),"-",B16&" kunder × "&B4&" kr = "&B17&" kr")',
        ],
        [
            "Estimeret profit/måned",
            '=IF(OR(B3="",B4=""), "-", B17-B3)',
            "Omsætning − budget",
            '=IF(OR(B3="",B4=""),"-",B17&" kr − "&B3&" kr = "&B18&" kr")',
        ],
        [
            "ROAS",
            '=IF(OR(B3="",B4=""), "-", ROUND(B17/B3,2)&"x")',
            "Omsætning ÷ budget",
            '=IF(OR(B3="",B4=""),"-",B17&" kr ÷ "&B3&" kr = "&B19)',
        ],
        ["", "", "", ""],
        [
            "STATUS",
            '=IF(OR(B3="",B4=""), "⚠️ Udfyld budget og fortjeneste", IF(B18>0, "✅ Profitable", "❌ Ikke profitable"))',
            "",
            "",
        ],
        ["", "", "", ""],
        ["💡 BEMÆRK", "", "", ""],
        ["", "", "", ""],
        ["Advokat-branchen har høje CPC'er (20-40 DKK)", "", "", ""],
        ["Men kundernes værdi er også høj", "", "", ""],
        ["Fokusér på High Intent keywords for bedste ROI", "", "", ""],
    ]

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'ROI Beregner'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": roi_rows},
    ).execute()
    print("  Written ROI calculator with formulas")

    # Calculate totals
    total_da_volume = sum(k["Avg. Monthly Searches"] for k in danish_keywords)
    total_en_volume = sum(k["Avg. Monthly Searches"] for k in english_keywords)
    high_intent_count = len([k for k in danish_keywords if k["Intent"] == "High"])

    print("\n" + "=" * 60)
    print("ENHANCED DELIVERABLE COMPLETE!")
    print("=" * 60)
    print(f"\nSpreadsheet URL: {spreadsheet_url}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print("\nSummary:")
    print(
        f"  Tab 1 - Danish Keywords: {len(danish_keywords)} keywords ({total_da_volume:,} total monthly searches)"
    )
    print(
        f"          High Intent: {high_intent_count} | Medium: {len([k for k in danish_keywords if k['Intent'] == 'Medium'])} | Low: {len([k for k in danish_keywords if k['Intent'] == 'Low'])}"
    )
    print(
        f"  Tab 2 - English Keywords: {len(english_keywords)} keywords ({total_en_volume:,} total monthly searches)"
    )
    print(f"  Tab 3 - Competitor Keywords: {len(competitor_keywords)} keywords")
    print(
        f"  Tab 4 - Campaign Structure: {len(campaign_structure)} keyword-to-ad-group mappings"
    )
    print(f"  Tab 5 - Ad Copy: {len(ads)} RSA ads")
    print("  Tab 6 - ROI Beregner: Interactive calculator")

    # Campaign breakdown
    campaigns = {}
    for row in campaign_structure:
        camp = row["Campaign"]
        if camp not in campaigns:
            campaigns[camp] = 0
        campaigns[camp] += 1

    print("\nCampaign Breakdown:")
    for camp, count in sorted(campaigns.items()):
        print(f"  {camp}: {count} keywords")


if __name__ == "__main__":
    main()
