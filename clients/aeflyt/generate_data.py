import os
import sys
import json
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from services.keyword_planner import KeywordPlannerService

def main():
    load_dotenv()
    
    # Initialize service
    try:
        service = KeywordPlannerService()
        print("Service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        return

    # Seed keywords based on website analysis
    seed_keywords = [
        "flyttefirma",
        "erhvervsflytning",
        "privatflytning",
        "flyttefirma sjælland",
        "erhvervsflytning sjælland",
        "flyttefirma københavn",
        "kontorflytning",
        "international flytning",
        "opbevaring møbler"
    ]

    print(f"Generating ideas for: {seed_keywords}")
    
    # Generate ideas
    try:
        ideas = service.generate_keyword_ideas(
            keywords=seed_keywords,
            location_ids=["Denmark"], # Target Denmark
            language_id="1009", # Danish
            customer_id="7562650658" # Use NMD Law ID for access
        )
        
        print(f"Generated {len(ideas)} ideas")
        
        # Save to file
        output_path = os.path.join(os.path.dirname(__file__), 'keyword_data_raw.json')
        with open(output_path, 'w') as f:
            json.dump(ideas, f, indent=4)
            
        print(f"Saved raw data to {output_path}")
        
    except Exception as e:
        print(f"Error generating ideas: {e}")

if __name__ == "__main__":
    main()
