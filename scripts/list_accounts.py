import os
import sys
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv

load_dotenv()

def list_accessible_customers():
    try:
        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True
        }
        
        # Initialize client without login_customer_id first
        client = GoogleAdsClient.load_from_dict(config)
        customer_service = client.get_service("CustomerService")
        
        print("Listing accessible customers...")
        accessible_customers = customer_service.list_accessible_customers()
        
        for resource_name in accessible_customers.resource_names:
            print(f"Customer resource name: {resource_name}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_accessible_customers()
