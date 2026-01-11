import os
from pathlib import Path
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.ads_connector import AdsConnector

def get_brand_id():
    load_dotenv(Path.home() / ".mondaybrew" / ".env")
    CUSTOMER_ID = "5207009970"
    connector = AdsConnector()
    print(f"--- Searching for Brand Campaign ID for {CUSTOMER_ID} ---")
    rows = connector.get_campaign_performance(CUSTOMER_ID, "LAST_30_DAYS")
    found = False
    for r in rows:
        if "Brand" in r['campaign_name']:
            print(f"FOUND: '{r['campaign_name']}' -> ID: {r['campaign_id']}")
            found = True
    if not found:
        print("No campaign with 'Brand' in name found.")

if __name__ == "__main__":
    get_brand_id()
