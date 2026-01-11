#!/usr/bin/env python3
"""
ROI Beregner v3 - Add ROI Calculator tab to Google Sheets deliverable.

Simplified for service businesses:
- Only 2 required inputs: Budget + Profit per customer
- No confusing "profit margin" - just ask what they earn per customer
- Smart defaults for close rate, CPC, website conv rate

v3 improvements:
- Percentage inputs as whole numbers (3 = 3%, 15 = 15%)
- ROAS as factor format (1.33x instead of 133%)
- Clear funnel distinction: conv rate (visitors→leads) vs close rate (leads→customers)
- Calculation explanations in notes column
- Removed hardcoded client-specific notes
"""

import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(Path.home() / ".mondaybrew" / ".env")

from backend.services.google_sheets import GoogleSheetsService


def delete_sheet_if_exists(sheets_service, spreadsheet_id: str, sheet_name: str):
    """Delete a sheet by name if it exists."""
    try:
        sheet_metadata = sheets_service.get(spreadsheetId=spreadsheet_id).execute()
        for sheet in sheet_metadata.get("sheets", []):
            if sheet["properties"]["title"] == sheet_name:
                sheet_id = sheet["properties"]["sheetId"]
                sheets_service.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"requests": [{"deleteSheet": {"sheetId": sheet_id}}]},
                ).execute()
                print(f"    Deleted existing '{sheet_name}' tab")
                return True
    except Exception:
        pass
    return False


def add_roi_tab_v2(
    spreadsheet_id: str,
    client_name: str = "Client",
    budget: int = 3000,
    profit_per_customer: int = 800,
    cpc: int = 8,
):
    """
    Add ROI Beregner v2 tab to an existing spreadsheet.

    Args:
        spreadsheet_id: The Google Sheet ID
        client_name: Client name for the title
        budget: Monthly ad budget in DKK (pre-filled)
        profit_per_customer: What they earn per customer in DKK
        cpc: Estimated CPC from keyword analysis
    """
    gs = GoogleSheetsService()
    sheets_service = gs.service.spreadsheets()

    print(f"[1/4] Setting up 'ROI Beregner' tab...")

    # Delete existing tab if it has errors
    delete_sheet_if_exists(sheets_service, spreadsheet_id, "ROI Beregner")

    # Create new sheet
    add_sheet_request = {
        "requests": [{"addSheet": {"properties": {"title": "ROI Beregner"}}}]
    }
    response = sheets_service.batchUpdate(
        spreadsheetId=spreadsheet_id, body=add_sheet_request
    ).execute()
    new_sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
    print(f"    Created new sheet with ID: {new_sheet_id}")

    print("[2/4] Writing ROI calculator structure...")

    # Build the data with FIXED formulas (no circular references!)
    # Layout matches plan: B5=budget, B6=profit, B7=close_rate, B10=cpc, B11=conv_rate
    # Results: B14=clicks, B15=leads, B16=customers, B17=revenue, B18=profit, B19=ROAS
    roi_data = [
        # Row 1-2: Title
        [f"ROI Beregner - {client_name}", "", "", ""],
        ["Beregn forventet afkast af dine Google Ads", "", "", ""],
        ["", "", "", ""],
        # Row 4: Section header
        ["📊 DINE TAL", "Værdi", "Hvad betyder det?", ""],
        # Row 5: Budget (REQUIRED)
        [
            "Månedligt annoncebudget",
            budget,
            "Hvor meget vil du bruge på Google Ads?",
            "",
        ],
        # Row 6: Profit per customer (REQUIRED)
        [
            "Fortjeneste pr. kunde",
            profit_per_customer,
            "Hvad tjener du på én kunde?",
            "",
        ],
        # Row 7: Close rate (whole number, default 15 = 15%)
        [
            "Lukningsrate %",
            15,
            "Hvor mange % af dine henvendelser bliver til salg?",
            "",
        ],
        # Row 8: Empty
        ["", "", "", ""],
        # Row 9: Section header
        ["📈 KAMPAGNE ESTIMATER", "Værdi", "Hvad betyder det?", ""],
        # Row 10: CPC (with default, from keyword analysis)
        [
            "Pris pr. klik (CPC)",
            cpc,
            "Hvad koster ét klik på din annonce?",
            "",
        ],
        # Row 11: Website conversion rate (whole number, default 3 = 3%)
        [
            "Website konverteringsrate %",
            3,
            "Hvor mange % af besøgende udfylder formularen?",
            "",
        ],
        # Row 12: Empty
        ["", "", "", ""],
        # Row 13: Section header
        ["🧮 BEREGNEDE RESULTATER", "Værdi", "Forklaring", "Beregning"],
        # Row 14: Clicks (Budget / CPC)
        [
            "Estimerede klik/måned",
            '=IF(B5="", "-", ROUND(B5 / IF(B10="", 8, B10), 0))',
            "Hvor mange klik kan du købe for dit budget?",
            '=IF(B5="", "", B5 & " kr ÷ " & B10 & " kr pr. klik = " & B14 & " klik")',
        ],
        # Row 15: Leads (Clicks × conv rate %)
        [
            "Estimerede leads/måned",
            '=IF(B5="", "-", ROUND(B14 * (IF(B11="", 3, B11) / 100), 1))',
            "Hvor mange udfylder kontaktformularen?",
            '=IF(B5="", "", B14 & " klik × " & B11 & "% = " & B15 & " leads")',
        ],
        # Row 16: Customers (Leads × close rate %)
        [
            "Estimerede kunder/måned",
            '=IF(B5="", "-", ROUND(B15 * (IF(B7="", 15, B7) / 100), 1))',
            "Hvor mange leads bliver til betalende kunder?",
            '=IF(B5="", "", B15 & " leads × " & B7 & "% = " & B16 & " kunder")',
        ],
        # Row 17: Revenue (Customers × profit per customer)
        [
            "Estimeret omsætning/måned",
            '=IF(OR(B5="", B6=""), "-", ROUND(B16 * B6, 0))',
            "Hvad tjener du på disse kunder?",
            '=IF(OR(B5="", B6=""), "", B16 & " kunder × " & B6 & " kr = " & B17 & " kr")',
        ],
        # Row 18: Profit (Revenue - Budget)
        [
            "Estimeret profit/måned",
            '=IF(OR(B5="", B6=""), "-", B17 - B5)',
            "Din fortjeneste efter annonceudgifter",
            '=IF(OR(B5="", B6=""), "", B17 & " kr − " & B5 & " kr = " & B18 & " kr")',
        ],
        # Row 19: ROAS (factor format: 1.33x)
        [
            "ROAS (Return on Ad Spend)",
            '=IF(OR(B5="", B6=""), "-", ROUND(B17 / B5, 2) & "x")',
            "For hver 1 kr brugt, får du X kr tilbage",
            '=IF(OR(B5="", B6=""), "", B17 & " kr ÷ " & B5 & " kr = " & ROUND(B17/B5, 2) & "x")',
        ],
        # Row 20: Empty
        ["", "", "", ""],
        # Row 21: Status
        [
            "STATUS",
            '=IF(OR(B5="", B6=""), "⚠️ Udfyld budget og fortjeneste", IF(B18>0, "✅ Profitable", "❌ Ikke profitable"))',
            '=IF(B18>0, "Du tjener penge på Google Ads! 🎉", IF(B18<0, "Du taber penge - juster dine tal", ""))',
            "",
        ],
    ]

    gs.write_sheet(spreadsheet_id, "ROI Beregner!A1", roi_data)
    print(f"    Wrote {len(roi_data)} rows with fixed formulas")

    print("[3/4] Applying formatting...")

    format_requests = [
        # Title formatting (Row 1) - Bold, larger font
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True, "fontSize": 16},
                    }
                },
                "fields": "userEnteredFormat.textFormat",
            }
        },
        # Subtitle (Row 2) - italic, gray
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "italic": True,
                            "foregroundColor": {"red": 0.4, "green": 0.4, "blue": 0.4},
                        },
                    }
                },
                "fields": "userEnteredFormat.textFormat",
            }
        },
        # Section header 1 (Row 4) - DINE TAL - blue background
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 3,
                    "endRowIndex": 4,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        },
                        "backgroundColor": {"red": 0.25, "green": 0.45, "blue": 0.7},
                    }
                },
                "fields": "userEnteredFormat.textFormat,userEnteredFormat.backgroundColor",
            }
        },
        # Section header 2 (Row 9) - KAMPAGNE ESTIMATER - teal background
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 8,
                    "endRowIndex": 9,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        },
                        "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.5},
                    }
                },
                "fields": "userEnteredFormat.textFormat,userEnteredFormat.backgroundColor",
            }
        },
        # Section header 3 (Row 13) - BEREGNEDE RESULTATER - green background
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 12,
                    "endRowIndex": 13,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        },
                        "backgroundColor": {"red": 0.2, "green": 0.55, "blue": 0.35},
                    }
                },
                "fields": "userEnteredFormat.textFormat,userEnteredFormat.backgroundColor",
            }
        },
        # Yellow background for INPUT cells (B5:B7) - editable
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 4,
                    "endRowIndex": 7,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat",
            }
        },
        # Yellow background for INPUT cells (B10:B11) - editable
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 9,
                    "endRowIndex": 11,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat",
            }
        },
        # Light green for CALCULATED results (B14:B19)
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 13,
                    "endRowIndex": 19,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat",
            }
        },
        # Gray italic for explanation column (C5:C7, C10:C11)
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 4,
                    "endRowIndex": 7,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "italic": True,
                            "foregroundColor": {"red": 0.4, "green": 0.4, "blue": 0.4},
                        },
                    }
                },
                "fields": "userEnteredFormat.textFormat",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 9,
                    "endRowIndex": 11,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "italic": True,
                            "foregroundColor": {"red": 0.4, "green": 0.4, "blue": 0.4},
                        },
                    }
                },
                "fields": "userEnteredFormat.textFormat",
            }
        },
        # Light gray background for calculation column (D14:D19)
        {
            "repeatCell": {
                "range": {
                    "sheetId": new_sheet_id,
                    "startRowIndex": 13,
                    "endRowIndex": 19,
                    "startColumnIndex": 3,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                        "textFormat": {"fontFamily": "Roboto Mono", "fontSize": 9},
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat",
            }
        },
        # Column widths
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": new_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 250},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": new_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2,
                },
                "properties": {"pixelSize": 120},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": new_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 2,
                    "endIndex": 3,
                },
                "properties": {"pixelSize": 320},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": new_sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 3,
                    "endIndex": 4,
                },
                "properties": {"pixelSize": 280},
                "fields": "pixelSize",
            }
        },
    ]

    # Conditional formatting for profit cell (B18) - Green if positive, Red if negative
    format_requests.append(
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": new_sheet_id,
                            "startRowIndex": 17,
                            "endRowIndex": 18,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_GREATER",
                            "values": [{"userEnteredValue": "0"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 0.7, "green": 0.9, "blue": 0.7}
                        },
                    },
                },
                "index": 0,
            }
        }
    )

    format_requests.append(
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": new_sheet_id,
                            "startRowIndex": 17,
                            "endRowIndex": 18,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_LESS_THAN_EQ",
                            "values": [{"userEnteredValue": "0"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 0.95, "green": 0.7, "blue": 0.7}
                        },
                    },
                },
                "index": 1,
            }
        }
    )

    sheets_service.batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": format_requests}
    ).execute()

    print("[4/4] Done!")
    print(f"\n{'='*60}")
    print("ROI Beregner v3 added successfully!")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print("=" * 60)

    # Print expected calculations for verification (using default rates)
    conv_rate = 3  # whole number (3%)
    close_rate = 15  # whole number (15%)

    clicks = budget / cpc
    leads = clicks * (conv_rate / 100)
    customers = leads * (close_rate / 100)
    revenue = customers * profit_per_customer
    profit = revenue - budget
    roas = revenue / budget if budget > 0 else 0

    print("\nExpected calculations (with defaults):")
    print(f"  Clicks: {budget} ÷ {cpc} = {clicks:.0f}")
    print(f"  Leads: {clicks:.0f} × {conv_rate}% = {leads:.1f}")
    print(f"  Customers: {leads:.1f} × {close_rate}% = {customers:.1f}")
    print(f"  Revenue: {customers:.1f} × {profit_per_customer} = {revenue:.0f} DKK")
    print(f"  Profit: {revenue:.0f} - {budget} = {profit:.0f} DKK")
    print(f"  ROAS: {roas:.2f}x")
    print(f"  Status: {'✅ Profitable' if profit > 0 else '❌ Ikke profitable'}")

    return spreadsheet_id


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_roi_tab.py <SPREADSHEET_ID> [CLIENT_NAME]")
        sys.exit(1)
        
    SPREADSHEET_ID = sys.argv[1]
    CLIENT_NAME = sys.argv[2] if len(sys.argv) > 2 else "Client"
    
    print(f"Adding ROI tab to Spreadsheet: {SPREADSHEET_ID} for Client: {CLIENT_NAME}")

    add_roi_tab_v2(
        spreadsheet_id=SPREADSHEET_ID,
        client_name=CLIENT_NAME,
        budget=3000,
        profit_per_customer=5000,  # Estimated for law services
        cpc=15,  # Estimated for law keywords
    )
