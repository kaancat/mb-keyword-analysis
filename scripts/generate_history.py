import sys
import os
import random
from datetime import datetime, timedelta
import uuid

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ads_connector import AdsConnector
from services.bigquery_manager import BigQueryManager
from dotenv import load_dotenv

load_dotenv()

def generate_fake_history():
    print("--- Generating Fake History (Metrics) ---")
    
    ads = AdsConnector()
    bq = BigQueryManager()
    
    # 1. Get the accounts we just created
    accounts = ads.get_accessible_customers()
    if not accounts:
        print("No accounts found. Did you run generate_structure.py?")
        return

    # 2. Ensure BigQuery Table Exists
    bq.ensure_campaign_table_exists()
    
    all_rows = []
    
    # Generate 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for account in accounts:
        customer_id = account['id']
        print(f"Generating history for Account: {account['name']} ({customer_id})")
        
        # We need campaign IDs. Since we can't easily fetch them without a complex query,
        # we will fetch them from the API first.
        real_campaigns = ads.get_campaign_performance(customer_id, date_range="LAST_30_DAYS")
        
        # If the API returns nothing (because they are new), we need to fetch the structure
        # using a different query that doesn't depend on metrics.
        # For simplicity in this script, we'll just query the Campaign resource directly.
        
        campaign_query = """
            SELECT campaign.id, campaign.name, campaign.status 
            FROM campaign 
            WHERE campaign.status != 'REMOVED'
        """
        campaign_rows = ads.client.get_service("GoogleAdsService").search_stream(
            customer_id=customer_id, query=campaign_query
        )
        
        campaigns = []
        for batch in campaign_rows:
            for row in batch.results:
                campaigns.append({
                    "id": str(row.campaign.id),
                    "name": row.campaign.name,
                    "status": row.campaign.status.name
                })
        
        if not campaigns:
            print("  No campaigns found in this account.")
            continue

        # Generate daily data for each campaign
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            for camp in campaigns:
                # Randomize metrics based on campaign name to make it realistic
                if "Brand" in camp['name']:
                    imps = random.randint(100, 500)
                    ctr = random.uniform(0.15, 0.25)
                    cpc = random.uniform(0.5, 1.5)
                    conv_rate = random.uniform(0.10, 0.20)
                elif "Competitor" in camp['name']:
                    imps = random.randint(50, 200)
                    ctr = random.uniform(0.02, 0.05)
                    cpc = random.uniform(3.0, 8.0)
                    conv_rate = random.uniform(0.02, 0.05)
                else: # Generic
                    imps = random.randint(500, 2000)
                    ctr = random.uniform(0.03, 0.08)
                    cpc = random.uniform(1.0, 3.0)
                    conv_rate = random.uniform(0.03, 0.06)
                
                clicks = int(imps * ctr)
                cost = clicks * cpc
                conversions = int(clicks * conv_rate)
                
                all_rows.append({
                    "customer_id": str(customer_id),
                    "campaign_id": camp['id'],
                    "campaign_name": camp['name'],
                    "status": camp['status'],
                    "date": date_str,
                    "cost": round(cost, 2),
                    "impressions": imps,
                    "clicks": clicks,
                    "conversions": conversions,
                    "ctr": round(ctr, 4),
                    "avg_cpc": round(cpc, 2),
                    "cpa": round(cost / conversions, 2) if conversions > 0 else 0
                })
            
            current_date += timedelta(days=1)

    # 3. Insert into BigQuery
    if all_rows:
        print(f"Inserting {len(all_rows)} rows of fake history into BigQuery...")
        bq.insert_campaign_data(all_rows)
        print("Done!")
    else:
        print("No data generated.")

if __name__ == "__main__":
    generate_fake_history()
