import os
import sys
from dotenv import load_dotenv

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ads_connector import AdsConnector

def analyze_strategy():
    load_dotenv()
    
    CUSTOMER_ID = "5207009970" # Karim Design
    DATE_RANGE = "LAST_30_DAYS" # Broader view for strategy
    
    print(f"--- Strategic Analysis: Karim Design ({CUSTOMER_ID}) ---")
    print(f"--- Range: {DATE_RANGE} ---\n")
    
    connector = AdsConnector()
    
    # 1. Auction Insights (Who is bidding on us?)
    print("--- 1. COMPETITOR LANDSCAPE (Auction Insights) ---")
    try:
        auction_df = connector.get_auction_insights(CUSTOMER_ID, DATE_RANGE)
        
        if not auction_df.empty:
            # Group by competitor domain across all campaigns
            competitors = auction_df.groupby('competitor_domain').mean(numeric_only=True).sort_values('impression_share', ascending=False)
            
            print(f"Top 5 Competitors by Impression Share:")
            print(competitors[['impression_share', 'outranking_share', 'overlap_rate']].head(5))
            
            # Check specifically for "Brand" campaigns if possible
            brand_auction = auction_df[auction_df['campaign_name'].str.contains('Brand', case=False, na=False)]
            if not brand_auction.empty:
                 print(f"\n[ALERT] Competitors on BRAND Campaigns:")
                 brand_comps = brand_auction.groupby('competitor_domain').mean(numeric_only=True).sort_values('impression_share', ascending=False)
                 print(brand_comps[['impression_share', 'outranking_share', 'overlap_rate']].head(5))
            else:
                 print("\nGood News: Low/No competitor pressure detected directly on Brand campaigns.")
        else:
            print("No Auction Insights data available.")
            
    except Exception as e:
        print(f"Error fetching Auction Insights: {e}")

    # 2. Budget Distribution Check
    print("\n--- 2. BUDGET & EFFICIENCY ---")
    campaigns = connector.get_campaign_performance(CUSTOMER_ID, DATE_RANGE)
    
    brand_spend = 0
    generic_spend = 0
    competitor_spend = 0
    
    brand_conv = 0
    generic_conv = 0
    competitor_conv = 0
    
    for c in campaigns:
        name = c['campaign_name'].lower()
        cost = c['cost']
        conv = c['conversions']
        
        if 'brand' in name:
            brand_spend += cost
            brand_conv += conv
        elif 'konkurrent' in name or 'competitor' in name:
            competitor_spend += cost
            competitor_conv += conv
        else: # Assumed generic
            generic_spend += cost
            generic_conv += conv
            
    total_spend = brand_spend + generic_spend + competitor_spend
    
    print(f"Brand Spend:      ${brand_spend:.2f} ({brand_spend/total_spend*100:.1f}%) | CPA: ${(brand_spend/brand_conv if brand_conv else 0):.2f}")
    print(f"Generic Spend:    ${generic_spend:.2f} ({generic_spend/total_spend*100:.1f}%) | CPA: ${(generic_spend/generic_conv if generic_conv else 0):.2f}")
    print(f"Competitor Spend: ${competitor_spend:.2f} ({competitor_spend/total_spend*100:.1f}%) | CPA: ${(competitor_spend/competitor_conv if competitor_conv else 0):.2f}")
    
    if competitor_spend > 0 and competitor_conv == 0:
        print("\n[RECOMMENDATION] Competitor campaign is burning cash with 0 return. Consider killing it.")

if __name__ == "__main__":
    analyze_strategy()
