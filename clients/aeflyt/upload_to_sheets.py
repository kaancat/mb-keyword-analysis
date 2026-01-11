import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from services.google_sheets import GoogleSheetsService

def main():
    load_dotenv()
    
    # Initialize service
    try:
        service = GoogleSheetsService()
        print("Google Sheets Service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        return

    # Create new spreadsheet
    try:
        sheet_id = service.create_spreadsheet("Aeflyt.dk - Potential Analysis")
        print(f"Created spreadsheet with ID: {sheet_id}")
        print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    except Exception as e:
        print(f"Failed to create spreadsheet: {e}")
        return

    base_dir = os.path.dirname(__file__)
    
    # Define tabs and files
    tabs = [
        {"name": "Keyword Analysis", "file": "keyword_analysis.json"},
        {"name": "Campaign Structure", "file": "campaign_structure.json"},
        {"name": "Ad Copy", "file": "ad_copy.json"},
        {"name": "ROI Calculator", "file": "roi_calculator.json"}
    ]
    
    for tab in tabs:
        file_path = os.path.join(base_dir, tab['file'])
        if not os.path.exists(file_path):
            print(f"Warning: File {tab['file']} not found. Skipping.")
            continue
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Prepare data for sheets (list of lists)
        values = []
        
        if tab['name'] == "ROI Calculator":
            # Special handling for ROI Calculator (Object structure)
            # We'll flatten it for display
            values.append(["ROI Calculator Inputs & Estimates"])
            values.append(["Metric", "Value"])
            
            inputs = data.get("client_inputs", {})
            for k, v in inputs.items():
                values.append([k, v])
                
            estimates = data.get("campaign_estimates", {})
            for k, v in estimates.items():
                values.append([k, v])
                
            values.append([])
            values.append(["Calculated Outputs"])
            outputs = data.get("calculated_outputs", {})
            for k, v in outputs.items():
                values.append([k, v])
                
        else:
            # List of objects structure
            if isinstance(data, list) and len(data) > 0:
                headers = list(data[0].keys())
                values.append(headers)
                for item in data:
                    row = [str(item.get(h, "")) for h in headers]
                    values.append(row)
            else:
                values.append(["No data"])

        # Create tab (if not first one which is created by default)
        # Note: Google Sheets creates "Sheet1" by default. We'll rename/add.
        # For simplicity in this script, we'll just write to new tabs.
        
        try:
            # Add sheet request
            body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": tab['name']
                        }
                    }
                }]
            }
            service.service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
            
            # Write data
            service.write_sheet(sheet_id, f"{tab['name']}!A1", values)
            print(f"Uploaded {tab['name']}")
            
        except Exception as e:
            print(f"Error uploading {tab['name']}: {e}")

    # Delete default Sheet1 if possible/desired, or just leave it.
    print(f"Done! Access the sheet here: https://docs.google.com/spreadsheets/d/{sheet_id}")

if __name__ == "__main__":
    main()
