#!/usr/bin/env python3
"""Create NMD Law Group Google Ads deliverable spreadsheet."""

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
        print(f"  REFRESH_TOKEN: {'SET' if refresh_token else 'MISSING'}")
        print(f"  CLIENT_ID: {'SET' if client_id else 'MISSING'}")
        print(f"  CLIENT_SECRET: {'SET' if client_secret else 'MISSING'}")
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

    # Load data
    with open("/tmp/nmd_tab1_keyword_analysis.json", "r", encoding="utf-8") as f:
        tab1_data = json.load(f)

    with open("/tmp/nmd_tab2_campaign_structure.json", "r", encoding="utf-8") as f:
        tab2_data = json.load(f)

    with open("/tmp/nmd_tab3_ad_copy.json", "r", encoding="utf-8") as f:
        tab3_data = json.load(f)

    # Create spreadsheet with 4 sheets
    print("Creating spreadsheet...")
    spreadsheet_body = {
        "properties": {
            "title": "[KEYWORD ANALYSIS & AD COPY] - NMD Law Group - Udlændingeret"
        },
        "sheets": [
            {"properties": {"title": "Keyword Analysis"}},
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
    for kw in tab1_data:
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
                "TRUE" if kw["Include"] else "FALSE",
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Keyword Analysis'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab1_rows},
    ).execute()
    print(f"  Written {len(tab1_rows)-1} keywords")

    # ============ TAB 2: Campaign Structure ============
    print("\nWriting Tab 2: Campaign Structure...")
    tab2_headers = ["Campaign", "Ad Group", "Keyword", "Match Type", "Final URL"]
    tab2_rows = [tab2_headers]
    for row in tab2_data:
        tab2_rows.append(
            [
                row["Campaign"],
                row["Ad Group"],
                row["Keyword"],
                row["Match Type"],
                row["Final URL"],
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Campaign Structure'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab2_rows},
    ).execute()
    print(f"  Written {len(tab2_rows)-1} keyword assignments")

    # ============ TAB 3: Ad Copy ============
    print("\nWriting Tab 3: Ad Copy...")
    tab3_headers = [
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
    tab3_rows = [tab3_headers]
    for ad in tab3_data:
        row = [
            ad["Campaign"],
            ad["Ad Group"],
            ad["Headline 1"],
            ad.get("Headline 1 position", ""),
            ad["Headline 2"],
            ad.get("Headline 2 position", ""),
            ad["Headline 3"],
            ad.get("Headline 3 position", ""),
            ad["Headline 4"],
            ad.get("Headline 4 position", ""),
            ad["Headline 5"],
            ad.get("Headline 5 position", ""),
            ad["Headline 6"],
            ad.get("Headline 6 position", ""),
            ad["Headline 7"],
            ad.get("Headline 7 position", ""),
            ad["Headline 8"],
            ad.get("Headline 8 position", ""),
            ad.get("Headline 9", ""),
            ad.get("Headline 9 position", ""),
            ad.get("Headline 10", ""),
            ad.get("Headline 10 position", ""),
            ad["Description 1"],
            ad.get("Description 1 position", ""),
            ad["Description 2"],
            ad.get("Description 2 position", ""),
            ad["Description 3"],
            ad.get("Description 3 position", ""),
            ad["Description 4"],
            ad.get("Description 4 position", ""),
            ad["Path 1"],
            ad["Path 2"],
            ad["Final URL"],
        ]
        tab3_rows.append(row)

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Ad Copy'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab3_rows},
    ).execute()
    print(f"  Written {len(tab3_rows)-1} RSA ads")

    # ============ TAB 4: ROI Beregner ============
    print("\nWriting Tab 4: ROI Beregner...")

    roi_rows = [
        ["📊 DINE TAL", "", "Hvad betyder det?", ""],
        ["", "", "", ""],
        ["Månedligt annoncebudget", "", "", ""],
        ["Fortjeneste pr. kunde", "", "Hvad tjener I pr. kunde?", ""],
        ["Lukningsrate %", "15", "Leads der bliver til kunder", ""],
        ["", "", "", ""],
        ["📈 KAMPAGNE ESTIMATER", "", "Hvad betyder det?", ""],
        ["", "", "", ""],
        ["Pris pr. klik (CPC)", "15", "Typisk for advokat-branchen", ""],
        ["Website konverteringsrate %", "3", "Besøgende der udfylder formular", ""],
        ["", "", "", ""],
        ["🧮 BEREGNEDE RESULTATER", "", "Forklaring", "Beregning"],
        ["", "", "", ""],
        [
            "Estimerede klik/måned",
            '=IF(B3="", "-", ROUND(B3/IF(B9="",15,B9),0))',
            "Budget ÷ CPC",
            '=IF(B3="","-",B3&" kr ÷ "&IF(B9="",15,B9)&" kr = "&B14&" klik")',
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
    ]

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'ROI Beregner'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": roi_rows},
    ).execute()
    print("  Written ROI calculator with formulas")

    print("\n" + "=" * 60)
    print("DELIVERABLE COMPLETE!")
    print("=" * 60)
    print(f"\nSpreadsheet URL: {spreadsheet_url}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print("\nSummary:")
    print(f"  Tab 1 - Keyword Analysis: {len(tab1_data)} keywords")
    print(
        f"  Tab 2 - Campaign Structure: {len(tab2_data)} keyword-to-ad-group mappings"
    )
    print(f"  Tab 3 - Ad Copy: {len(tab3_data)} RSA ads")
    print("  Tab 4 - ROI Beregner: Interactive calculator")


if __name__ == "__main__":
    main()
