import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def debug_access():
    # Load .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    
    customer_id = "3135586021"
    
    print(f"Debugging access for Customer ID: {customer_id}")
    
    # 1. Try with current env (Manager Login)
    print("\n[1] Testing with current Manager Login...")
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True
        })
        
        ga_service = client.get_service("GoogleAdsService")
        query = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                print(f"Success! Connected to: {row.customer.descriptive_name} ({row.customer.id})")
                
    except GoogleAdsException as ex:
        print(f"Failed: {ex.error.code().name if hasattr(ex, 'error') else ex}")

    # 2. Try as Direct Login (login_customer_id = customer_id)
    print("\n[2] Testing as Direct Login (login_customer_id = target)...")
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": customer_id, # Use the test account as login
            "use_proto_plus": True
        })
        
        ga_service = client.get_service("GoogleAdsService")
        query = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                print(f"Success! Connected to: {row.customer.descriptive_name} ({row.customer.id})")
                
    except GoogleAdsException as ex:
        print(f"Failed: {ex.error.code().name if hasattr(ex, 'error') else ex}")

    # 3. Try without login_customer_id
    print("\n[3] Testing without login_customer_id...")
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            # No login_customer_id
            "use_proto_plus": True
        })
        
        ga_service = client.get_service("GoogleAdsService")
        query = "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                print(f"Success! Connected to: {row.customer.descriptive_name} ({row.customer.id})")
                
    except GoogleAdsException as ex:
        print(f"Failed: {ex.error.code().name if hasattr(ex, 'error') else ex}")

    # 4. Debug SitelinkAsset fields
    print("\n[4] Debugging SitelinkAsset fields...")
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True
        })
        sitelink = client.get_type("SitelinkAsset")
        print("SitelinkAsset fields:", dir(sitelink))
        # Check if final_urls exists
        if hasattr(sitelink, 'final_urls'):
            print("Has 'final_urls'")
        else:
            print("Does NOT have 'final_urls'")
            
    except Exception as e:
        print(f"Error inspecting SitelinkAsset: {e}")

if __name__ == "__main__":
    debug_access()
