import os
from pathlib import Path
import sys

# Ensure we are running from the root directory context for imports
sys.path.append(os.getcwd() + "/backend")

from dotenv import load_dotenv
from services.google_sheets import GoogleSheetsService

# Load environment variables
load_dotenv(Path.home() / ".mondaybrew" / ".env")

def test_sheets_connection():
    print("--- Testing Google Sheets Connection ---")
    
    # 1. Initialize Service
    try:
        service = GoogleSheetsService()
        print("Service initialized successfully.")
    except Exception as e:
        print(f"ERROR initializing service: {e}")
        return

    # 2. Test Read (User's Template)
    # URL: https://docs.google.com/spreadsheets/d/1nvFhMi_mDqZVqc6elbdHecWOTkX0dQZ6TgU-41LvWU8/edit
    spreadsheet_id = "1nvFhMi_mDqZVqc6elbdHecWOTkX0dQZ6TgU-41LvWU8"
    range_name = "Keywords!A1:E5" # Reading first 5 rows of Keywords tab
    
    print(f"\nAttempting to read from Sheet ID: {spreadsheet_id}")
    print(f"Range: {range_name}")
    
    values = service.read_sheet(spreadsheet_id, range_name)
    
    if values:
        print("\nSUCCESS: Read data from sheet:")
        for row in values:
            print(row)
    else:
        print("\nFAILED: Could not read data. Check permissions/scopes.")

if __name__ == "__main__":
    test_sheets_connection()
