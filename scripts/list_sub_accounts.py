import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def list_sub_accounts():
    # Load .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    
    # Manager Account ID
    manager_customer_id = "3135586021"
    
    # Override Login Customer ID to be the Manager Account
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
        
        print(f"Listing sub-accounts for Manager ID: {manager_customer_id}")
        
        service = client.get_service("GoogleAdsService")
        query = """
            SELECT
                customer_client.client_customer,
                customer_client.level,
                customer_client.manager,
                customer_client.descriptive_name,
                customer_client.id,
                customer_client.status
            FROM customer_client
            WHERE customer_client.level <= 1
        """
        
        response = service.search(customer_id=manager_customer_id, query=query)
        
        print(f"{'ID':<15} | {'Name':<30} | {'Manager':<8} | {'Status':<10}")
        print("-" * 70)
        
        found_client = False
        for row in response:
            c = row.customer_client
            print(f"{c.id:<15} | {c.descriptive_name:<30} | {str(c.manager):<8} | {c.status.name:<10}")
            
            if not c.manager and c.status.name == 'ENABLED':
                found_client = True
                print(f"\n>>> FOUND VALID CLIENT ACCOUNT: {c.id}")
                # We could break here, but let's list all
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_sub_accounts()
