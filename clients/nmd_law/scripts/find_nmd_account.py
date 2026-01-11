import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize the Google Ads client
    try:
        # Load from env but manually add missing key if needed
        config_data = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": "8959543272",
            "use_proto_plus": True
        }
        client = GoogleAdsClient.load_from_dict(config_data)
    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed with status "
              f"'{ex.error.code().name}' and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        return

    # MCC ID to search under
    mcc_id = "8959543272" # Mondaybrew MCC (Test/Prod) - using the one that worked for keyword planner
    
    # GAQL query to find accounts with "NMD" in the name
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

    ga_service = client.get_service("GoogleAdsService")

    try:
        response = ga_service.search(customer_id=mcc_id, query=query)
        
        print(f"Searching for 'NMD' accounts under MCC {mcc_id}...")
        found = False
        for row in response:
            customer = row.customer_client
            if "NMD" in customer.descriptive_name or "nmd" in customer.descriptive_name.lower():
                print(f"FOUND: {customer.descriptive_name} (ID: {customer.id})")
                print(f"  - Currency: {customer.currency_code}")
                print(f"  - Timezone: {customer.time_zone}")
                found = True
                
        if not found:
            print("No accounts found matching 'NMD'. Listing all accounts:")
            # Reset iterator or re-query if needed, but for now just print not found.
            # Let's re-run to list all if not found, just in case name is different.
            response = ga_service.search(customer_id=mcc_id, query=query)
            for row in response:
                 print(f"  - {row.customer_client.descriptive_name} ({row.customer_client.id})")

    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed with status "
              f"'{ex.error.code().name}' and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")

if __name__ == "__main__":
    main()
