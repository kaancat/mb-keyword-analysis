import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_user_lists():
    load_dotenv(Path.home() / ".mondaybrew" / ".env")
    
    CUSTOMER_ID = "5207009970" # Karim Design
    
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": "True",
    }
    
    client = GoogleAdsClient.load_from_dict(config)
    ga_service = client.get_service("GoogleAdsService")
    
    query = """
        SELECT
            user_list.id,
            user_list.name,
            user_list.type,
            user_list.size_for_search,
            user_list.size_for_display
        FROM user_list
        WHERE user_list.membership_status = 'OPEN'
    """
    
    print(f"--- Fetching User Lists for {CUSTOMER_ID} ---")
    
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        
        found = False
        for batch in response:
            for row in batch.results:
                found = True
                ul = row.user_list
                print(f"ID: {ul.id} | Name: '{ul.name}' | Type: {ul.type_.name} | Search Size: {ul.size_for_search}")
        
        if not found:
            print("No enabled user lists found.")
            
    except GoogleAdsException as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    get_user_lists()
