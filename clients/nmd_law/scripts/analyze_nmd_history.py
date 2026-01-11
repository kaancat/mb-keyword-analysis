import os
import csv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

load_dotenv()

def main():
    # Configuration
    CUSTOMER_ID = "7562650658" # NMD Law Group
    LOGIN_CUSTOMER_ID = "8959543272" # Mondaybrew MCC
    
    # Initialize client
    config_data = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": LOGIN_CUSTOMER_ID,
        "use_proto_plus": True
    }
    client = GoogleAdsClient.load_from_dict(config_data)
    ga_service = client.get_service("GoogleAdsService")
    
    print(f"Fetching historical data for Customer ID: {CUSTOMER_ID}...")
    
    # 1. Campaign Performance (Last 3 Years)
    # Segments: Year, Month
    query = """
        SELECT
          campaign.id,
          campaign.name,
          segments.year,
          segments.month,
          metrics.cost_micros,
          metrics.impressions,
          metrics.clicks,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '2022-01-01' AND '2024-11-30'
        ORDER BY segments.year DESC, segments.month DESC
    """
    
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
        
        data = []
        for row in response:
            cost = row.metrics.cost_micros / 1_000_000
            data.append({
                "Campaign": row.campaign.name,
                "Year": row.segments.year,
                "Month": row.segments.month,
                "Cost": cost,
                "Impressions": row.metrics.impressions,
                "Clicks": row.metrics.clicks,
                "Conversions": row.metrics.conversions,
                "Conv. Value": row.metrics.conversions_value,
                "CPC": cost / row.metrics.clicks if row.metrics.clicks > 0 else 0,
                "CPA": cost / row.metrics.conversions if row.metrics.conversions > 0 else 0
            })
            
        # Save to CSV
        output_file = "output/nmd_historical_performance.csv"
        keys = data[0].keys() if data else []
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
            
        print(f"Saved {len(data)} rows to {output_file}")
        
        # 2. Search Terms Analysis (Last 12 Months) - Identify wasted spend
        print("\nFetching Search Terms (Last 12 Months)...")
        query_st = """
            SELECT
              search_term_view.search_term,
              metrics.cost_micros,
              metrics.clicks,
              metrics.conversions
            FROM search_term_view
            WHERE segments.date BETWEEN '2023-11-30' AND '2024-11-30'
            ORDER BY metrics.cost_micros DESC
            LIMIT 100
        """
        response_st = ga_service.search(customer_id=CUSTOMER_ID, query=query_st)
        
        st_data = []
        for row in response_st:
            cost = row.metrics.cost_micros / 1_000_000
            st_data.append({
                "Search Term": row.search_term_view.search_term,
                "Cost": cost,
                "Clicks": row.metrics.clicks,
                "Conversions": row.metrics.conversions,
                "CPA": cost / row.metrics.conversions if row.metrics.conversions > 0 else 0
            })
            
        output_file_st = "output/nmd_search_terms.csv"
        keys_st = st_data[0].keys() if st_data else []
        with open(output_file_st, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys_st)
            writer.writeheader()
            writer.writerows(st_data)
            
        print(f"Saved {len(st_data)} search terms to {output_file_st}")

        # 3. Basic Analysis Summary
        total_spend = sum(d["Cost"] for d in data)
        total_conv = sum(d["Conversions"] for d in data)
        avg_cpa = total_spend / total_conv if total_conv > 0 else 0
        
        print("\n--- Quick Analysis Summary (2022-2024) ---")
        print(f"Total Spend: {total_spend:.2f} DKK")
        print(f"Total Conversions: {total_conv:.1f}")
        print(f"Average CPA: {avg_cpa:.2f} DKK")
        
        # Wasted spend (Terms with > 0 spend and 0 conversions)
        wasted_spend = sum(d["Cost"] for d in st_data if d["Conversions"] == 0)
        print(f"Wasted Spend (Top 100 Terms, Last 12M): {wasted_spend:.2f} DKK")
        
    except GoogleAdsException as ex:
        print(f"Request failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"\t{error.message}")

if __name__ == "__main__":
    main()
