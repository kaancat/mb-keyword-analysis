import os
import re
import json
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Load environment variables
load_dotenv()

# Configuration
CUSTOMER_ID = "5912422766"  # Test Account ID from README
# In a real scenario, we might use the login customer ID or a specific client ID
# If 5912422766 is a test account, it might not return real volume data (it often returns 0 or mock data).
# However, the user explicitly asked to use the API credentials.
# We will use the env var GOOGLE_ADS_LOGIN_CUSTOMER_ID if available and look for accessible customers,
# but for the plan service, we often need a real account ID.
# Let's prioritize the env var if it looks like a standard account, else fallback to the one in README.

ENV_CUSTOMER_ID = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
if ENV_CUSTOMER_ID and ENV_CUSTOMER_ID.replace("-", "").isdigit():
    CUSTOMER_ID = ENV_CUSTOMER_ID.replace("-", "")

LOCATION_ID = "2208"  # Denmark
LANGUAGE_ID = "1009"  # Danish

REQUIRED_ENV_VARS = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
]

def check_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

def load_keywords_from_md(file_path):
    """Extracts keywords from the markdown file bullet points."""
    keywords = []
    tier_map = {}
    
    current_tier = "Unknown"
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Detect Headers for Tiers
                line_upper = line.upper()
                if "TIER 1" in line_upper:
                    current_tier = "Tier 1"
                elif "TIER 2" in line_upper:
                    current_tier = "Tier 2"
                elif "TIER 3" in line_upper:
                    current_tier = "Tier 3"
                elif "TIER 4" in line_upper:
                    current_tier = "Tier 4"
                elif "TIER 5" in line_upper:
                    current_tier = "Tier 5"
                elif "TIER 7" in line_upper:
                    current_tier = "Tier 7"
                
                # Extract bullet points
                if line.startswith("- ") or line.startswith("* "):
                    # Clean up the line: remove "- ", quotes, etc.
                    clean_line = line.lstrip("- *").strip()
                    
                    # New Parsing Logic:
                    # 1. Look for content inside quotes "keyword"
                    match_quotes = re.search(r'"(.*?)"', clean_line)
                    if match_quotes:
                         keyword = match_quotes.group(1).lower().strip()
                    else:
                         # 2. Fallback: Take everything before any '(' or just the whole line if no parens
                         # and remove specific markdown chars like `**` if present
                         clean_line_no_bold = clean_line.replace("**", "")
                         keyword = re.split(r'\(', clean_line_no_bold)[0].strip().lower()

                    if len(keyword) > 2 and "keyword" not in keyword and "[" not in keyword: # Basic filter
                        keywords.append(keyword)
                        tier_map[keyword] = current_tier
                        
        print(f"Loaded {len(keywords)} keywords from {file_path}")
        return list(set(keywords)), tier_map # Remove duplicates
    except FileNotFoundError:
        print(f"Error: File not found {file_path}")
        sys.exit(1)

def get_keyword_metrics(client, customer_id, keywords):
    """Calls the Google Ads API KeywordPlanIdeaService to get historical metrics."""
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    
    # We use generate_keyword_historical_metrics to get volume for specific keywords
    # Instead of generate_keyword_ideas which suggests NEW keywords.
    # However, historical metrics request requires a list of keywords.
    
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = customer_id
    request.keywords = keywords
    request.geo_target_constants.append(f"geoTargetConstants/{LOCATION_ID}")
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    request.language = f"languageConstants/{LANGUAGE_ID}"
    
    results_map = {}
    
    try:
        response = keyword_plan_idea_service.generate_keyword_historical_metrics(request=request)
        
        for result in response.results:
            metrics = result.keyword_metrics
            
            # Extract AVG CPC
            # Note: API returns micros (divide by 1,000,000)
            low_bid = metrics.low_top_of_page_bid_micros / 1000000.0 if metrics.low_top_of_page_bid_micros else 0.0
            high_bid = metrics.high_top_of_page_bid_micros / 1000000.0 if metrics.high_top_of_page_bid_micros else 0.0
            
            results_map[result.text] = {
                "avg_searches": metrics.avg_monthly_searches if metrics.avg_monthly_searches else 0,
                "competition": metrics.competition.name, # LOW, MEDIUM, HIGH
                "low_bid": low_bid,
                "high_bid": high_bid,
                "competition_index": metrics.competition_index
            }
            
    except GoogleAdsException as ex:
        print(f"API Error: {ex}")
        # Identify specific errors
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
            if error.message == "The customer account is a test account.":
                print("WARNING: Using a Test Account. Google Ads Test Accounts often return EMPTY metrics for Keyword Planning.")
                
    return results_map

def main():
    check_env()
    
    # Initialize Client
    try:
        config_dict = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True
        }
        # If accessing via MCC, login_customer_id is needed
        if os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"):
             config_dict["login_customer_id"] = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
             
        client = GoogleAdsClient.load_from_dict(config_dict)
    except Exception as e:
        print(f"Failed to initialize Google Ads Client: {e}")
        sys.exit(1)

    # Load Keywords
    md_path = "clients/mondaybrew/initial_keywords.md"
    keywords, tier_map = load_keywords_from_md(md_path)
    
    if not keywords:
        print("No keywords found to process.")
        sys.exit(1)
        
    print(f"Fetching metrics for {len(keywords)} keywords...")
    print(f"Keywords: {keywords}")
    print(f"Using Customer ID: {CUSTOMER_ID}")
    
    # Batch requests if essential (limit is large, but good practice)
    # The limit is usually around 2000 keywords per request. We have less.
    metrics_data = get_keyword_metrics(client, CUSTOMER_ID, keywords)
    
    # Build JSON Output
    output_data = []
    
    for kw in keywords:
        # Default data if API returned nothing (e.g. strict match fail or volume too low)
        data = metrics_data.get(kw, {
            "avg_searches": -1,
            "competition": "UNKNOWN",
            "low_bid": 0.0,
            "high_bid": 0.0
        })
        
        # Determine Category/Intent based on Tier
        tier = tier_map.get(kw, "Unknown")
        intent = "High" if tier in ["Tier 1", "Tier 4"] else "Medium"
        include = True if tier in ["Tier 1", "Tier 4", "Tier 2"] else False
        if tier == "Tier 3": include = False
        
        category = "General"
        if "virker ikke" in kw or "problem" in kw: category = "Pain Points"
        if "bureau" in kw: category = "Agency"
        if "google ads" in kw and "pris" in kw: category = "Pricing"
        
        entry = {
            "Keyword": kw,
            "Tier": tier,
            "Avg. Monthly Searches": data["avg_searches"],
            "Competition": data["competition"],
            "Top of page bid (low range)": f"DKK {data['low_bid']:.2f}",
            "Top of page bid (high range)": f"DKK {data['high_bid']:.2f}",
            "Category": category,
            "Intent": intent,
            "Include": include
        }
        output_data.append(entry)
        
    # Sort: Tier 1 & 4 first, then by searches
    def sort_key(item):
        tier_prio = 3
        if item["Tier"] == "Tier 1": tier_prio = 0
        if item["Tier"] == "Tier 4": tier_prio = 1
        if item["Tier"] == "Tier 2": tier_prio = 2
        return (tier_prio, -item["Avg. Monthly Searches"])
        
    output_data.sort(key=sort_key)
    
    # Save to JSON
    output_file = "clients/mondaybrew/keyword_analysis.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Successfully saved analysis to {output_file}")

if __name__ == "__main__":
    main()
