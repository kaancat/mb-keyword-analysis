import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ads_connector import AdsConnector
from backend.services.ga4_service import GA4Service

def run_audit(customer_id, ga4_property_id=None, ga4_domain=None):
    print(f"--- Starting Audit for Customer ID: {customer_id} ---")
    
    ads_connector = AdsConnector()
    ga4_service = GA4Service()
    
    audit_data = {
        "metadata": {
            "customer_id": customer_id,
            "audit_date": datetime.now().isoformat(),
            "ga4_property_id": ga4_property_id,
            "ga4_domain": ga4_domain,
        },
        "google_ads": {},
        "ga4": {}
    }
    
    # 1. Fetch Google Ads Data
    print("Fetching Google Ads Data...")
    try:
        audit_data["google_ads"]["campaigns"] = ads_connector.get_campaign_performance(customer_id)
        audit_data["google_ads"]["ad_groups"] = ads_connector.get_ad_group_performance(customer_id)
        audit_data["google_ads"]["keywords"] = ads_connector.get_keyword_performance(customer_id)
        audit_data["google_ads"]["search_terms"] = ads_connector.get_search_terms(customer_id)
        audit_data["google_ads"]["ads"] = ads_connector.get_ad_performance(customer_id)
        audit_data["google_ads"]["asset_performance"] = ads_connector.get_asset_performance(customer_id)
        audit_data["google_ads"]["landing_pages"] = ads_connector.get_landing_page_performance(customer_id)
        audit_data["google_ads"]["expanded_landing_pages"] = ads_connector.get_expanded_landing_page_performance(customer_id)
        audit_data["google_ads"]["geographic"] = ads_connector.get_geographic_performance(customer_id)
        audit_data["google_ads"]["user_locations"] = ads_connector.get_user_location_performance(customer_id)
        audit_data["google_ads"]["devices"] = ads_connector.get_device_performance(customer_id)
        audit_data["google_ads"]["demographics"] = ads_connector.get_demographic_performance(customer_id)
        audit_data["google_ads"]["ad_schedule"] = ads_connector.get_ad_schedule_performance(customer_id)
        audit_data["google_ads"]["audiences"] = ads_connector.get_audience_performance(customer_id)
        audit_data["google_ads"]["impression_share"] = ads_connector.get_impression_share_data(customer_id)
        audit_data["google_ads"]["budgets"] = ads_connector.get_campaign_budgets(customer_id)
        audit_data["google_ads"]["bidding_strategies"] = ads_connector.get_bidding_strategies(customer_id)
        audit_data["google_ads"]["paid_organic"] = ads_connector.get_paid_organic_performance(customer_id)
        audit_data["google_ads"]["click_data"] = ads_connector.get_click_data(customer_id)
        audit_data["google_ads"]["conversion_actions"] = ads_connector.get_conversion_actions(customer_id)
        audit_data["google_ads"]["change_history"] = ads_connector.get_change_history(customer_id)
        audit_data["google_ads"]["recommendations"] = ads_connector.get_recommendations(customer_id)
    except Exception as e:
        print(f"Error fetching Ads data: {e}")
        
    # 2. GA4 Auto-Discovery & Fetch
    resolved_ga4_property_id = ga4_property_id

    if not resolved_ga4_property_id:
        if ga4_domain:
            # Try to auto-map GA4 property based on website domain
            print(f"Attempting to auto-discover GA4 Property by domain: {ga4_domain} ...")
            try:
                matches = ga4_service.find_properties_by_domain(ga4_domain)
            except Exception as e:
                print(f"Error during GA4 domain matching: {e}")
                matches = []

            audit_data["ga4"]["domain_matches"] = matches

            if matches:
                selected = matches[0]
                resolved_ga4_property_id = selected["property_id"]
                audit_data["metadata"]["ga4_property_id"] = resolved_ga4_property_id
                print(
                    f"Using GA4 property {resolved_ga4_property_id} "
                    f"({selected.get('display_name', 'unknown')}) for domain {ga4_domain}"
                )
            else:
                print(
                    f"No GA4 properties matched domain {ga4_domain}. "
                    "Listing all accessible properties instead..."
                )
                props = ga4_service.list_properties()
                print(f"Found {len(props)} accessible GA4 properties.")
                audit_data["ga4"]["available_properties"] = props
        else:
            # No GA4 ID and no domain hint: just list what we can see
            print("No GA4 property ID or domain provided. Listing accessible GA4 properties...")
            props = ga4_service.list_properties()
            print(f"Found {len(props)} accessible GA4 properties.")
            audit_data["ga4"]["available_properties"] = props

    if resolved_ga4_property_id:
        print(f"Fetching GA4 Data for Property: {resolved_ga4_property_id}...")
        try:
            audit_data["ga4"]["behavior"] = ga4_service.get_behavior_metrics(resolved_ga4_property_id)
            audit_data["ga4"]["conversions"] = ga4_service.get_conversion_breakdown(resolved_ga4_property_id)
            audit_data["ga4"]["top_pages"] = ga4_service.get_top_pages(resolved_ga4_property_id)
            audit_data["ga4"]["traffic_sources"] = ga4_service.get_traffic_sources(resolved_ga4_property_id)
        except Exception as e:
            print(f"Error fetching GA4 data: {e}")

    # Normalize any pandas DataFrame payloads to JSON-serializable structures
    try:
        import pandas as pd  # Local import to avoid hard dependency if not installed

        def _normalize(obj):
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient="records")
            return obj

        audit_data["google_ads"] = {
            key: _normalize(val) for key, val in audit_data.get("google_ads", {}).items()
        }
        audit_data["ga4"] = {key: _normalize(val) for key, val in audit_data.get("ga4", {}).items()}
    except Exception as e:
        print(f"Warning: Failed to normalize DataFrame outputs ({e}); falling back to raw objects.")

    # 3. Generate Outputs
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    # JSON Output
    json_path = os.path.join(output_dir, f"audit_{customer_id}_{date_str}.json")
    with open(json_path, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"JSON Report saved to: {json_path}")
    
    # Markdown Output
    md_path = os.path.join(output_dir, f"audit_{customer_id}_{date_str}.md")
    generate_markdown_report(audit_data, md_path)
    print(f"Markdown Report saved to: {md_path}")
    
    return json_path, md_path

def generate_markdown_report(data, filepath):
    ads = data.get("google_ads", {})
    ga4 = data.get("ga4", {})
    
    with open(filepath, "w") as f:
        f.write(f"# Account Audit Report: {data['metadata']['customer_id']}\n")
        f.write(f"**Date:** {data['metadata']['audit_date']}\n\n")
        
        # Executive Summary
        total_cost = sum(c['cost'] for c in ads.get('campaigns', []))
        total_conv = sum(c['conversions'] for c in ads.get('campaigns', []))
        cpa = total_cost / total_conv if total_conv > 0 else 0
        
        f.write("## 1. Executive Summary (Last 30 Days)\n")
        f.write(f"- **Total Spend:** {total_cost:.2f}\n")
        f.write(f"- **Total Conversions:** {total_conv:.1f}\n")
        f.write(f"- **Average CPA:** {cpa:.2f}\n\n")
        
        # Campaign Performance
        f.write("## 2. Campaign Performance\n")
        f.write("| Campaign | Status | Cost | Conv. | CPA | ROAS |\n")
        f.write("|----------|--------|------|-------|-----|------|\n")
        for c in ads.get('campaigns', []):
            cpa = c['cpa']
            f.write(f"| {c['campaign_name']} | {c['status']} | {c['cost']:.2f} | {c['conversions']} | {cpa:.2f} | - |\n")
        f.write("\n")
        
        # Keyword Health
        f.write("## 3. Keyword Health & Quality Score\n")
        keywords = ads.get('keywords', [])
        low_qs = [k for k in keywords if k['quality_score'] > 0 and k['quality_score'] < 5]
        f.write(f"- **Total Keywords:** {len(keywords)}\n")
        f.write(f"- **Low Quality Score (<5):** {len(low_qs)}\n\n")
        
        if low_qs:
            f.write("### Low Quality Score Keywords\n")
            f.write("| Keyword | QS | Campaign | Clicks | Cost |\n")
            f.write("|---------|----|----------|--------|------|\n")
            for k in low_qs[:10]: # Top 10
                f.write(f"| {k['keyword']} | {k['quality_score']} | {k['campaign_name']} | {k['clicks']} | {k['cost']:.2f} |\n")
            f.write("\n")
            
        # Search Terms
        f.write("## 4. Search Term Analysis\n")
        terms = ads.get('search_terms', [])
        f.write(f"- **Total Search Terms:** {len(terms)}\n")
        f.write("### Top Search Terms by Spend\n")
        f.write("| Search Term | Match Type | Cost | Conv. | CPA |\n")
        f.write("|-------------|------------|------|-------|-----|\n")
        for t in terms[:10]:
            f.write(f"| {t['search_term']} | {t['match_type']} | {t['cost']:.2f} | {t['conversions']} | {t['cpa']:.2f} |\n")
        f.write("\n")
        
        # GA4 Data
        if ga4.get('behavior'):
            f.write("## 5. GA4 Behavior Metrics\n")
            f.write("| Channel | Sessions | Eng. Rate | Conv. |\n")
            f.write("|---------|----------|-----------|-------|\n")
            for b in ga4['behavior']:
                f.write(f"| {b['channel']} | {b['sessions']} | {b['engagement_rate']} | {b['conversions']} |\n")
            f.write("\n")

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run Google Ads Account Audit")
    parser.add_argument("--customer-id", required=True, help="Google Ads Customer ID")
    parser.add_argument("--ga4-property-id", help="GA4 Property ID (Optional)")
    parser.add_argument("--ga4-domain", help="Client website domain for GA4 auto-mapping (Optional, e.g. example.com)")
    
    args = parser.parse_args()
    
    run_audit(args.customer_id, args.ga4_property_id, args.ga4_domain)
