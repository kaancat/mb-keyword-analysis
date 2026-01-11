import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.ads_connector import AdsConnector
# from config import GOOGLE_ADS_CUSTOMER_ID

# NMD Law Group ID
NMD_CUSTOMER_ID = "7562650658"
# MondayBrew MCC ID
MCC_ID = "8959543272"

def audit_conversions():
    # Ensure login customer ID is set correctly for MCC access
    os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = MCC_ID
    connector = AdsConnector()
    
    print(f"--- Auditing Conversion Actions for Account {NMD_CUSTOMER_ID} ---")
    
    query = """
        SELECT 
            conversion_action.id, 
            conversion_action.name, 
            conversion_action.type, 
            conversion_action.status,
            conversion_action.category
        FROM conversion_action
        WHERE conversion_action.status = 'ENABLED'
    """
    
    try:
        # Use get_conversion_actions method if available or raw search
        # connector.get_conversion_actions(NMD_CUSTOMER_ID)
        
        # Using raw search as per original script intent but with correct method signature if needed
        # Actually AdsConnector has get_conversion_actions, let's use that instead of raw search for simplicity
        print("Querying Google Ads API...")
        response = connector.get_conversion_actions(NMD_CUSTOMER_ID)
        print(f"Response received: {len(response) if response else 'None'}")
        
        if not response:
            print("No enabled conversion actions found.")
            return

        print(f"{'ID':<15} | {'Name':<40} | {'Type':<20} | {'Category'}")
        print("-" * 100)
        for row in response:
            # row is a dict from get_conversion_actions
            print(f"{row['id']:<15} | {row['name']:<40} | {row['type']:<20} | {row['category']}")
            
    except Exception as e:
        print(f"Error querying Google Ads: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting audit_nmd_ads.py...")
    try:
        audit_conversions()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
