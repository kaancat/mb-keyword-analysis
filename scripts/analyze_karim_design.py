import os
import sys
from dotenv import load_dotenv

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ads_connector import AdsConnector

def analyze_karim_design():
    load_dotenv()
    
    # Karim Design Customer ID
    CUSTOMER_ID = "5207009970"
    DATE_RANGE = "LAST_14_DAYS"
    
    print(f"--- Analysis for Karim Design ({CUSTOMER_ID}) ---")
    print(f"--- Date Range: {DATE_RANGE} ---\n")
    
    try:
        connector = AdsConnector()
        
        # 1. Campaign Performance
        campaigns = connector.get_campaign_performance(CUSTOMER_ID, DATE_RANGE)
        
        total_cost = 0
        total_conversions = 0
        total_clicks = 0
        
        print("--- 1. CAMPAIGN PERFORMANCE ---")
        for camp in campaigns:
            total_cost += camp['cost']
            total_conversions += camp['conversions']
            total_clicks += camp['clicks']
            
            cpa = camp['cost'] / camp['conversions'] if camp['conversions'] > 0 else 0
            roas = (camp.get('conversions_value', 0) / camp['cost']) if camp['cost'] > 0 else 0 # Assuming value might be there, if not it defaults 0
            
            if camp['cost'] > 0 or camp['conversions'] > 0:
                 print(f"CAMPAIGN: {camp['campaign_name']} ({camp['status']})")
                 print(f"  Cost: ${camp['cost']:.2f} | Convs: {camp['conversions']} | CPA: ${cpa:.2f}")
        
        print(f"\nTOTALS: Cost: ${total_cost:.2f} | Convs: {total_conversions} | Clicks: {total_clicks}\n")

        # 2. Keyword Performance (Quality Scores)
        print("--- 2. KEYWORD PERFORMANCE (Low QS / High Spend) ---")
        keywords = connector.get_keyword_performance(CUSTOMER_ID, DATE_RANGE)
        
        # Filter for active keywords with spend > 0
        active_kws = [k for k in keywords if k['status'] == 'ENABLED' and k['cost'] > 0]
        
        if active_kws:
            # Sort by Spend
            active_kws.sort(key=lambda x: x['cost'], reverse=True)
            
            for k in active_kws[:10]: # Top 10 spenders
                qs = k['quality_score']
                print(f"KW: '{k['keyword']}' ({k['match_type']}) | QS: {qs}/10")
                print(f"  Cost: ${k['cost']:.2f} | Convs: {k['conversions']} | Campaign: {k['campaign_name']}")
                if qs < 5 and qs > 0:
                    print(f"  [ALERT] Low Quality Score! (Exp. CTR: {k['expected_ctr']}, Landing Page: {k['landing_page_qs']})")
        else:
            print("No active keywords with spend found.")

        print("\n")

        # 3. Ad Performance
        print("--- 3. AD PERFORMANCE (Top Winners) ---")
        ads = connector.get_ad_performance(CUSTOMER_ID, DATE_RANGE)
        
        # Filter for ads with conversions
        converting_ads = [a for a in ads if a['conversions'] > 0]
        converting_ads.sort(key=lambda x: x['conversions'], reverse=True)
        
        if converting_ads:
            for ad in converting_ads[:3]:
                print(f"AD (Strength: {ad.get('ad_strength', 'N/A')}): {ad['ad_group_name']}")
                print(f"  Convs: {ad['conversions']} | Cost: ${ad['cost']:.2f}")
                # Print first 2 headlines
                if ad['headlines']:
                    h_texts = [h['text'] for h in ad['headlines'][:2]]
                    print(f"  Headlines: {' | '.join(h_texts)}")
        else:
            print("No ads with conversions found in this period.")

        # 4. Search Terms (Wasted Spend)
        print("\n--- 4. SEARCH TERMS (Wasted Spend Candidates) ---")
        terms = connector.get_search_terms(CUSTOMER_ID, DATE_RANGE)
        
        # Look for high cost, 0 conversions
        wasted = [t for t in terms if t['conversions'] == 0 and t['cost'] > 50]
        wasted.sort(key=lambda x: x['cost'], reverse=True)
        
        if wasted:
            for t in wasted[:5]:
                print(f"TERM: '{t['search_term']}' | Cost: ${t['cost']:.2f} | 0 Conversions")
        else:
            print("No significant wasted spend terms found (> $50).")

    except Exception as e:
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    analyze_karim_design()
