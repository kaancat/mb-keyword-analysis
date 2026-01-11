import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def main():
    spreadsheet_id = "1E68DCs_aOi342dLaPTD4CBlMnheKuG-AB_Jw8srYeDc"
    
    # Check env vars
    refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

    if not all([refresh_token, client_id, client_secret]):
        print("ERROR: Missing credentials")
        return

    # Initialize credentials
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    
    service = build("sheets", "v4", credentials=creds)
    
    # Load data
    with open("output/nmd_keywords_tab.json", "r") as f:
        keywords_data = json.load(f)
    with open("output/nmd_campaign_structure_tab.json", "r") as f:
        structure_data = json.load(f)
    with open("output/nmd_ads_tab.json", "r") as f:
        ads_data = json.load(f)
        
    # 1. Clear Sheet (or just overwrite)
    # We'll overwrite specific ranges. Ideally we should clear first but overwriting is safer if we don't want to delete tabs.
    # Actually, let's try to ensure tabs exist.
    
    # Helper to write data
    def write_tab(tab_name, data, headers):
        print(f"Writing {tab_name}...")
        rows = [headers]
        for item in data:
            row = []
            for h in headers:
                row.append(item.get(h, ""))
            rows.append(row)
            
        body = {
            "values": rows
        }
        
        try:
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"'{tab_name}'!A1",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            print(f"  Updated {tab_name} with {len(rows)-1} rows.")
        except Exception as e:
            print(f"  Error updating {tab_name}: {e}")

    # Tab 1: Keyword Analysis
    kw_headers = [
        "Campaign", "Ad Group", "Keyword", "Match Type", 
        "Avg. Monthly Searches", "Competition", 
        "Top of page bid (low range)", "Top of page bid (high range)", 
        "Intent", "Include"
    ]
    write_tab("Keyword Analysis", keywords_data, kw_headers)
    
    # Tab 2: Campaign Structure
    struct_headers = [
        "Campaign", "Ad Group", "Keyword", "Match Type", "Final URL"
    ]
    write_tab("Campaign Structure", structure_data, struct_headers)
    
    # Tab 3: Ad Copy
    ad_headers = ["Campaign", "Ad Group", "Final URL"]
    for i in range(1, 16):
        ad_headers.append(f"Headline {i}")
        ad_headers.append(f"Headline {i} position")
    for i in range(1, 5):
        ad_headers.append(f"Description {i}")
        ad_headers.append(f"Description {i} position")
    ad_headers.append("Path 1")
    ad_headers.append("Path 2")
    
    write_tab("Ad Copy", ads_data, ad_headers)
    
    print("Sheet update complete.")

if __name__ == "__main__":
    main()
