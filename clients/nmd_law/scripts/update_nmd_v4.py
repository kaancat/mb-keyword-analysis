#!/usr/bin/env python3
"""Update NMD Law Group Google Ads deliverable to V4 - Ultra-focused for 3000 DKK budget."""

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
    # Spreadsheet to update
    spreadsheet_id = "1E68DCs_aOi342dLaPTD4CBlMnheKuG-AB_Jw8srYeDc"

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

    # Load v4 data
    with open("/tmp/nmd_v4_keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)

    with open("/tmp/nmd_v4_campaign_structure.json", "r", encoding="utf-8") as f:
        campaign_structure = json.load(f)

    with open("/tmp/nmd_v4_ads.json", "r", encoding="utf-8") as f:
        ads = json.load(f)

    with open("/tmp/nmd_v4_negatives.json", "r", encoding="utf-8") as f:
        negatives = json.load(f)

    # Get existing sheet info
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing_sheets = {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in spreadsheet["sheets"]
    }

    print(f"\nExisting sheets: {list(existing_sheets.keys())}")

    # Define new sheet structure
    new_sheets = [
        "Keyword Analysis",
        "Campaign Structure",
        "Ad Copy",
        "Negative Keywords",
        "ROI Beregner",
    ]

    # Delete sheets that need to be recreated (to clear all data)
    requests = []
    for sheet_name in list(existing_sheets.keys()):
        if sheet_name not in ["ROI Beregner"]:  # Keep ROI, will update it
            requests.append({"deleteSheet": {"sheetId": existing_sheets[sheet_name]}})

    # Add new sheets
    for i, sheet_name in enumerate(new_sheets):
        if sheet_name != "ROI Beregner":  # ROI already exists
            requests.append(
                {"addSheet": {"properties": {"title": sheet_name, "index": i}}}
            )

    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
        print("Sheets restructured")

    # ============ TAB 1: Keyword Analysis ============
    print("\nWriting Tab 1: Keyword Analysis...")
    tab1_headers = [
        "Keyword",
        "Match Type",
        "Ad Group",
        "Est. Monthly Searches",
        "Competition",
        "Intent",
        "Rationale",
    ]
    tab1_rows = [tab1_headers]

    for kw in keywords:
        tab1_rows.append(
            [
                kw["Keyword"],
                kw["Match Type"],
                kw["Ad Group"],
                kw["Avg. Monthly Searches"],
                kw["Competition"],
                kw["Intent"],
                kw["Rationale"],
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
    tab2_headers = [
        "Campaign",
        "Ad Group",
        "Keyword",
        "Match Type",
        "Final URL",
        "Intent",
        "Est. Monthly Searches",
    ]
    tab2_rows = [tab2_headers]

    for row in campaign_structure:
        tab2_rows.append(
            [
                row["Campaign"],
                row["Ad Group"],
                row["Keyword"],
                row["Match Type"],
                row["Final URL"],
                row["Intent"],
                row["Est. Monthly Searches"],
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
        "H1 Pin",
        "Headline 2",
        "H2 Pin",
        "Headline 3",
        "H3 Pin",
        "Headline 4",
        "H4 Pin",
        "Headline 5",
        "H5 Pin",
        "Headline 6",
        "H6 Pin",
        "Headline 7",
        "H7 Pin",
        "Headline 8",
        "H8 Pin",
        "Headline 9",
        "H9 Pin",
        "Headline 10",
        "H10 Pin",
        "Headline 11",
        "H11 Pin",
        "Headline 12",
        "H12 Pin",
        "Headline 13",
        "H13 Pin",
        "Headline 14",
        "H14 Pin",
        "Headline 15",
        "H15 Pin",
        "Description 1",
        "D1 Pin",
        "Description 2",
        "D2 Pin",
        "Description 3",
        "D3 Pin",
        "Description 4",
        "D4 Pin",
        "Path 1",
        "Path 2",
        "Final URL",
    ]
    tab3_rows = [tab3_headers]

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
            ad.get("Headline 11", ""),
            ad.get("Headline 11 position", ""),
            ad.get("Headline 12", ""),
            ad.get("Headline 12 position", ""),
            ad.get("Headline 13", ""),
            ad.get("Headline 13 position", ""),
            ad.get("Headline 14", ""),
            ad.get("Headline 14 position", ""),
            ad.get("Headline 15", ""),
            ad.get("Headline 15 position", ""),
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
        tab3_rows.append(row)

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Ad Copy'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab3_rows},
    ).execute()
    print(f"  Written {len(tab3_rows)-1} RSA ads")

    # ============ TAB 4: Negative Keywords ============
    print("\nWriting Tab 4: Negative Keywords...")
    tab4_headers = ["Keyword", "Match Type", "Category", "Reason"]
    tab4_rows = [tab4_headers]

    category_reasons = {
        "Free Seekers": "Block people looking for free services/DIY",
        "DIY": "Block people trying to do it themselves",
        "Informational": "Block pure information seekers",
        "Job Seekers": "Block job seekers, not immigration clients",
        "Gov Seekers": "Block people looking for government sites",
        "Education": "Block people looking for courses/training",
        "Irrelevant": "Block unrelated services",
        "Competitors": "Block competitor brand searches",
        "Price Shoppers": "Block extreme price shoppers",
    }

    for neg in negatives:
        tab4_rows.append(
            [
                neg["Keyword"],
                neg["Match Type"],
                neg["Category"],
                category_reasons.get(neg["Category"], ""),
            ]
        )

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Negative Keywords'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": tab4_rows},
    ).execute()
    print(f"  Written {len(tab4_rows)-1} negative keywords")

    # ============ TAB 5: ROI Beregner (Updated for 3000 DKK) ============
    print("\nWriting Tab 5: ROI Beregner...")

    # Clear existing ROI tab first
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range="'ROI Beregner'!A1:Z100",
    ).execute()

    roi_rows = [
        ["NMD LAW GROUP - ROI BEREGNER", "", "", ""],
        [
            "Budget: 3000 DKK/måned | Fokus: Arbejdstilladelse & Familiesammenføring",
            "",
            "",
            "",
        ],
        ["", "", "", ""],
        ["📊 DINE TAL", "", "Forklaring", ""],
        ["", "", "", ""],
        ["Månedligt budget (DKK)", 3000, "Dit Google Ads budget", ""],
        [
            "Fortjeneste pr. kunde (DKK)",
            15000,
            "Typisk honorar for immigrationssag",
            "",
        ],
        ["Lukningsrate %", 25, "Leads der bliver til kunder (advokat ~25%)", ""],
        ["", "", "", ""],
        ["📈 KAMPAGNE ESTIMATER", "", "Forklaring", ""],
        ["", "", "", ""],
        ["Pris pr. klik (CPC)", 25, "Typisk for udlændingeret", ""],
        ["Website konverteringsrate %", 5, "Besøgende der kontakter jer", ""],
        ["", "", "", ""],
        ["🧮 BEREGNEDE RESULTATER", "", "Forklaring", "Beregning"],
        ["", "", "", ""],
        [
            "Estimerede klik/måned",
            "=ROUND(B6/B12,0)",
            "Budget ÷ CPC",
            '=B6&" kr ÷ "&B12&" kr = "&B17&" klik"',
        ],
        [
            "Estimerede leads/måned",
            "=ROUND(B17*(B13/100),1)",
            "Klik × konverteringsrate",
            '=B17&" klik × "&B13&"% = "&B18&" leads"',
        ],
        [
            "Estimerede kunder/måned",
            "=ROUND(B18*(B8/100),1)",
            "Leads × lukningsrate",
            '=B18&" leads × "&B8&"% = "&B19&" kunder"',
        ],
        [
            "Estimeret omsætning/måned",
            "=ROUND(B19*B7,0)",
            "Kunder × fortjeneste",
            '=B19&" × "&B7&" kr = "&B20&" kr"',
        ],
        [
            "Estimeret profit/måned",
            "=B20-B6",
            "Omsætning − budget",
            '=B20&" kr − "&B6&" kr = "&B21&" kr"',
        ],
        [
            "ROAS",
            '=IF(B20>0,ROUND(B20/B6,1)&"x","-")',
            "Return on Ad Spend",
            '=B20&" kr ÷ "&B6&" kr = "&B22',
        ],
        ["", "", "", ""],
        ["STATUS", '=IF(B21>0,"✅ PROFITABLE","❌ Ikke profitable")', "", ""],
        ["", "", "", ""],
        ["💡 V4 STRATEGI BEMÆRKNINGER", "", "", ""],
        ["", "", "", ""],
        ["• Ultra-fokuseret: Kun 13 high-intent keywords", "", "", ""],
        ["• 2 ad groups: Arbejdstilladelse & Familiesammenføring", "", "", ""],
        ["• Phrase match for reach på lille budget", "", "", ""],
        ["• 28 negative keywords blokerer spildtrafik", "", "", ""],
        ["• ~4 klik/dag = hvert klik tæller", "", "", ""],
        ["", "", "", ""],
        ["⚠️ MED 3000 DKK BUDGET:", "", "", ""],
        ["• Forvent 3-4 leads/måned", "", "", ""],
        ["• Fokus på kvalitet, ikke kvantitet", "", "", ""],
        ["• Monitor search terms ugentligt", "", "", ""],
        ["• Tilføj negatives løbende", "", "", ""],
    ]

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'ROI Beregner'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": roi_rows},
    ).execute()
    print("  Written ROI calculator with 3000 DKK budget")

    # ============ SUMMARY ============
    print("\n" + "=" * 70)
    print("NMD LAW GROUP V4 DELIVERABLE COMPLETE!")
    print("=" * 70)
    print(
        f"\nSpreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    )
    print("\n📊 V4 STRUCTURE (Ultra-focused for 3000 DKK/month):")
    print("-" * 50)
    print(f"  Campaign: mb | DA | Search | Udlændingeret")
    print(f"  Ad Groups: 2")
    print(f"  Keywords: {len(keywords)} (all HIGH INTENT)")
    print(f"  Ads: {len(ads)} RSAs")
    print(f"  Negative Keywords: {len(negatives)}")
    print("\n📈 EXPECTED RESULTS:")
    print("-" * 50)
    print(f"  Budget: 3000 DKK/month")
    print(f"  Clicks: ~120/month (~4/day)")
    print(f"  Leads: 3-4/month")
    print(f"  Keyword volume: 640 monthly searches")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
