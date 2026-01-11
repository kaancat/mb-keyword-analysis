import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.keyword_planner import KeywordPlannerService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set MCC ID
os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = "8959543272"

def run_keyword_research():
    kp = KeywordPlannerService()
    
    # Define seed keywords for different categories
    categories = {
        "permanent_ophold": [
            "permanent opholdstilladelse", 
            "permanent ophold", 
            "permanent opholdstilladelse regler",
            "krav til permanent opholdstilladelse"
        ],
        "familiesammenfoering": [
            "familiesammenføring", 
            "ægtefællesammenføring", 
            "familiesammenføring regler",
            "familiesammenføring eu regler"
        ],
        "opholdstilladelse": [
            "opholdstilladelse", 
            "opholdstilladelse danmark", 
            "forlængelse af opholdstilladelse",
            "arbejdstilladelse danmark"
        ],
        "advokat_udlaendingeret": [
            "advokat udlændingeret",
            "udlændinge advokat",
            "advokat opholdstilladelse",
            "advokat familiesammenføring"
        ],
        "english_expat": [
            "permanent residence denmark",
            "family reunification denmark",
            "residence permit denmark",
            "immigration lawyer denmark",
            "work permit denmark"
        ]
    }
    
    all_results = {}
    
    print("Starting keyword research...")
    
    for category, seeds in categories.items():
        print(f"Fetching keywords for category: {category} with seeds: {seeds}")
        
        # Determine language ID (1009 for Danish, 1000 for English)
        lang_id = "1000" if category == "english_expat" else "1009"
        
        try:
            results = kp.generate_keyword_ideas(
                keywords=seeds,
                location_ids=[2208],  # Denmark
                language_id=lang_id,
                # page_url="https://www.nmdlawgroup.com/udlaendingeret", # Removed to force keyword seed usage
                customer_id="8959543272" # Use accessible account
            )
            
            # Simple filtering/processing
            processed_results = []
            for item in results:
                # Keep only relevant fields
                processed_results.append({
                    "text": item.get("text"),
                    "avg_monthly_searches": item.get("avg_monthly_searches"),
                    "competition": item.get("competition"),
                    "low_top_of_page_bid_micros": item.get("low_top_of_page_bid_micros"),
                    "high_top_of_page_bid_micros": item.get("high_top_of_page_bid_micros")
                })
            
            # Sort by volume
            processed_results.sort(key=lambda x: x.get("avg_monthly_searches", 0) or 0, reverse=True)
            
            all_results[category] = processed_results
            print(f"Found {len(processed_results)} keywords for {category}")
            
        except Exception as e:
            print(f"Error fetching for {category}: {e}")
            
    # Save results
    output_file = "output/nmd_keyword_research_raw.json"
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print(f"Research complete. Results saved to {output_file}")

if __name__ == "__main__":
    run_keyword_research()
