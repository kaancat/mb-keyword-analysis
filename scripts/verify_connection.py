import os
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_connection():
    print("--- Verifying Google Ads Connection ---")
    
    # Check for required env vars
    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        return

    # Initialize the client
    try:
        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": "True"
        }
        client = GoogleAdsClient.load_from_dict(config)
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    
    print(f"Attempting to connect to MCC: {customer_id}")

    ga_service = client.get_service("GoogleAdsService")
    
    # Query to list sub-accounts
    query = """
        SELECT
            customer_client.client_customer,
            customer_client.level,
            customer_client.manager,
            customer_client.descriptive_name,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.id
        FROM customer_client
        WHERE customer_client.level <= 1
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        
        print("\n--- Connection Successful! ---")
        print(f"Connected to MCC {customer_id}. Found the following accounts:\n")
        
        count = 0
        for batch in response:
            for row in batch.results:
                count += 1
                client = row.customer_client
                print(f"[{count}] {client.descriptive_name} (ID: {client.id})")
                
        print(f"\nTotal Accounts Found: {count}")
        print("-" * 60)
        
    except GoogleAdsException as ex:
        print(f"\nRequest with ID '{ex.request_id}' failed with status '{ex.error.code().name}' and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    verify_connection()
