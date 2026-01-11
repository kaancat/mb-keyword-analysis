import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ads_connector import AdsConnector

def main():
    load_dotenv()
    
    print("--- Verifying Google Ads Access ---")
    print(f"Developer Token: {os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')[:5]}...")
    print(f"Login Customer ID: {os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')}")
    
    try:
        connector = AdsConnector()
        print("\nAttempting to fetch accessible customers...")
        customers = connector.get_accessible_customers()
        
        if customers:
            print(f"\nSUCCESS! Found {len(customers)} accessible accounts:")
            for c in customers:
                print(f"- {c['name']} ({c['id']})")
        else:
            print("\nSUCCESS! Connected, but no accessible accounts found (or only MCC itself).")
            
    except Exception as e:
        print(f"\nFAILED: {e}")

if __name__ == "__main__":
    main()
