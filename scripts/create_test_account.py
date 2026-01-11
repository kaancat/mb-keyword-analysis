import os
import sys
import time
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def create_test_account():
    # Load .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    
    # Manager Account ID
    manager_customer_id = "3135586021"
    os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = manager_customer_id
    
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True
        })
        
        print(f"Creating new test account under Manager ID: {manager_customer_id}")
        
        account_service = client.get_service("AccountBudgetProposalService") # Not this one
        # We need CustomerService to create a new customer
        # Actually, to create a new account under a manager, we use AccountLinkService? 
        # No, we use CustomerService.create_customer_client
        
        customer_service = client.get_service("CustomerService")
        customer_client = client.get_type("Customer")
        
        timestamp = int(time.time())
        customer_client.descriptive_name = f"Test Client Account {timestamp}"
        customer_client.currency_code = "USD"
        customer_client.time_zone = "America/New_York"
        
        # The relation is defined by creating it "under" the manager
        # But wait, create_customer_client is a method on CustomerService?
        # Let's check the docs or available methods.
        # It seems we need to use 'create_customer_client' method.
        
        response = customer_service.create_customer_client(
            customer_id=manager_customer_id,
            customer_client=customer_client
        )
        
        new_customer_resource = response.resource_name
        new_customer_id = new_customer_resource.split('/')[-1]
        
        print(f"Successfully created new client account!")
        print(f"Resource Name: {new_customer_resource}")
        print(f"Customer ID: {new_customer_id}")
        print("\nPlease update your test script to use this Customer ID.")

    except Exception as e:
        print(f"Error creating account: {e}")

if __name__ == "__main__":
    create_test_account()
