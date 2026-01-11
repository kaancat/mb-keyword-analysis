#!/usr/bin/env python3
"""
Upload Guld Design Local Services deliverable to Google Sheets.
Creates a new spreadsheet with 3 tabs following Monday Brew schema.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from backend.services.google_sheets import GoogleSheetsService


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    gs = GoogleSheetsService()

    # Create new spreadsheet
    print("[1/4] Creating new spreadsheet...")
    spreadsheet_id = gs.create_spreadsheet(
        "[KEYWORD ANALYSIS & AD COPY] - Guld Design (Local Services)"
    )

    if not spreadsheet_id:
        print("ERROR: Failed to create spreadsheet")
        return

    print(f"    Spreadsheet ID: {spreadsheet_id}")
    print(f"    URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    # Add additional sheets (Sheet1 already exists)
    print("[2/4] Adding tabs...")
    sheets_service = gs.service.spreadsheets()

    # Rename Sheet1 to "Keyword Analysis" and add other sheets
    requests = [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": 0, "title": "Keyword Analysis"},
                "fields": "title",
            }
        },
        {"addSheet": {"properties": {"title": "Campaign Structure"}}},
        {"addSheet": {"properties": {"title": "Ad Copy"}}},
    ]

    sheets_service.batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()

    # Load data
    print("[3/4] Loading JSON data...")
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
    )

    tab1_data = load_json(os.path.join(output_dir, "guld_tab1_keyword_analysis.json"))
    tab2_data = load_json(os.path.join(output_dir, "guld_tab2_campaign_structure.json"))
    tab3_data = load_json(os.path.join(output_dir, "guld_tab3_ad_copy.json"))

    # Tab 1: Keyword Analysis
    print("[4/4] Writing data to sheets...")

    # Build Tab 1 rows
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
                kw.get("Keyword", ""),
                kw.get("Avg. Monthly Searches", 0),
                kw.get("YoY Change", ""),
                kw.get("Competition", ""),
                kw.get("Top of page bid (low range)", ""),
                kw.get("Top of page bid (high range)", ""),
                kw.get("Category", ""),
                kw.get("Intent", ""),
                "TRUE" if kw.get("Include") else "FALSE",
            ]
        )

    gs.write_sheet(spreadsheet_id, "Keyword Analysis!A1", tab1_rows)
    print(f"    Tab 1: {len(tab1_rows)-1} keywords written")

    # Build Tab 2 rows
    tab2_headers = ["Campaign", "Ad Group", "Keyword", "Match Type", "Final URL"]
    tab2_rows = [tab2_headers]
    for entry in tab2_data:
        tab2_rows.append(
            [
                entry.get("Campaign", ""),
                entry.get("Ad Group", ""),
                entry.get("Keyword", ""),
                entry.get("Match Type", ""),
                entry.get("Final URL", ""),
            ]
        )

    gs.write_sheet(spreadsheet_id, "Campaign Structure!A1", tab2_rows)
    print(f"    Tab 2: {len(tab2_rows)-1} keyword entries written")

    # Build Tab 3 rows
    tab3_headers = [
        "Campaign",
        "Ad Group",
        "Final URL",
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
    ]
    tab3_rows = [tab3_headers]
    for ad in tab3_data:
        row = [
            ad.get("Campaign", ""),
            ad.get("Ad Group", ""),
            ad.get("Final URL", ""),
        ]
        # Headlines 1-8 with positions
        for i in range(1, 9):
            row.append(ad.get(f"Headline {i}", ""))
            row.append(ad.get(f"Headline {i} position", ""))
        # Descriptions 1-4 with positions
        for i in range(1, 5):
            row.append(ad.get(f"Description {i}", ""))
            row.append(ad.get(f"Description {i} position", ""))
        # Paths
        row.append(ad.get("Path 1", ""))
        row.append(ad.get("Path 2", ""))
        tab3_rows.append(row)

    gs.write_sheet(spreadsheet_id, "Ad Copy!A1", tab3_rows)
    print(f"    Tab 3: {len(tab3_rows)-1} ad copy entries written")

    print("\n" + "=" * 60)
    print("DONE! Spreadsheet created successfully.")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
