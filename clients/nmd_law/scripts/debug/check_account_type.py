import os
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

# Add parent directory to path to import config if needed, though we use .env here
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

load_dotenv()

def check_account_type(customer_id):
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }

    print(f"Checking Account ID: {customer_id}")
    print(f"Using Login Customer ID: {config['login_customer_id']}")

    try:
        client = GoogleAdsClient.load_from_dict(config)
        
        # We need to query the Customer resource
        # We can use the GoogleAdsService to search for the customer
        ga_service = client.get_service("GoogleAdsService")

        query = f"""
            SELECT 
                customer.id, 
                customer.descriptive_name, 
                customer.manager, 
                customer.status,
                customer.currency_code,
                customer.time_zone
            FROM customer
            WHERE customer.id = {customer_id}
        """

        # Note: We must issue the search request against the customer_id we are querying
        # OR against the login_customer_id if we are looking for a child.
        # Let's try querying the customer_id directly first.
        
        print("\n--- Querying Customer Resource ---")
        stream = ga_service.search_stream(customer_id=customer_id, query=query)

        found = False
        for batch in stream:
            for row in batch.results:
                found = True
                c = row.customer
                print(f"ID: {c.id}")
                print(f"Name: {c.descriptive_name}")
                print(f"Is Manager Account?: {c.manager}")
                print(f"Status: {c.status.name}")
                print(f"Currency: {c.currency_code}")
                print(f"Time Zone: {c.time_zone}")
                
                if c.manager:
                    print("\n⚠️ WARNING: This is a Manager Account (MCC). You CANNOT upload conversions to it.")
                    print("You must use the Client Account ID.")
                else:
                    print("\n✅ This is a Client Account. Conversion uploads should work.")

        if not found:
            print(f"\n❌ Account {customer_id} found, but no rows returned (this is unusual).")

    except GoogleAdsException as ex:
        print(f"\n❌ Request Failed for {customer_id}")
        print(f"Error: {ex}")
        for error in ex.failure.errors:
            print(f"  - {error.message}")
            print(f"  - Error Code: {error.error_code}")

if __name__ == "__main__":
    # The ID in question
    target_id = "7562650658"
    check_account_type(target_id)
