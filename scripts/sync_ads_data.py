import sys
import os
from pathlib import Path

# Add backend directory to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ads_connector import AdsConnector
from services.bigquery_manager import BigQueryManager
from dotenv import load_dotenv

load_dotenv(Path.home() / ".mondaybrew" / ".env")

def sync_data():
    print("--- Starting Data Sync ---")
    
    try:
        ads = AdsConnector()
        bq = BigQueryManager()
        
        # 1. Ensure Table Exists
        bq.ensure_campaign_table_exists()
        
        # 2. Get All Accounts
        accounts = ads.get_accessible_customers()
        print(f"Found {len(accounts)} accounts.")
        
        total_rows = 0
        
        for account in accounts:
            customer_id = account['id']
            name = account['name']
            print(f"Syncing Account: {name} ({customer_id})...")
            
            # 3. Fetch Data (Default: Last 30 Days)
            rows = ads.get_campaign_performance(customer_id, date_range="LAST_30_DAYS")
            
            if rows:
                # 4. Insert into BigQuery
                bq.insert_campaign_data(rows)
                total_rows += len(rows)
            else:
                print("  No data found.")
                
        print("-" * 40)
        print(f"Sync Complete. Total Rows Inserted: {total_rows}")
        print("-" * 40)
        
    except Exception as e:
        print(f"Critical Error during sync: {e}")

if __name__ == "__main__":
    sync_data()
