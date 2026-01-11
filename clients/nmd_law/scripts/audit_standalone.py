import os
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()

# Hardcoded config for debugging
CUSTOMER_ID = "7562650658"
MCC_ID = "8959543272"
CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")

def main():
    print("Starting self-contained audit...")
    
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, DEVELOPER_TOKEN]):
        print("Missing environment variables!")
        return

    try:
        credentials = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        client = GoogleAdsClient(
            credentials=credentials,
            developer_token=DEVELOPER_TOKEN,
            login_customer_id=MCC_ID,
            version="v19"
        )
        
        print(f"Client initialized. Querying customer {CUSTOMER_ID}...")
        
        ga_service = client.get_service("GoogleAdsService")
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
        
        response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
        
        print(f"{'ID':<15} | {'Name':<40} | {'Type':<20} | {'Category'}")
        print("-" * 100)
        
        count = 0
        for row in response:
            count += 1
            c = row.conversion_action
            print(f"{c.id:<15} | {c.name:<40} | {c.type_:<20} | {c.category}")
            
        print(f"Found {count} conversion actions.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
