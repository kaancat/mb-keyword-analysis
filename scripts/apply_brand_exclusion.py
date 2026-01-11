import os
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_exclusion():
    load_dotenv()
    
    # --- HARDCODED CONFIGURATION ---
    # Customer: Karim Design
    CUSTOMER_ID = "5207009970" 
    
    # Campaign: MB | Brand
    CAMPAIGN_ID = "17488875745"
    
    # Audience: Purchasers of Karimdesign.dk - GA4 (Remarketing)
    USER_LIST_ID = "7196486736"
    # --------------------------------
    
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": "True",
    }
    
    client = GoogleAdsClient.load_from_dict(config)
    
    # Service client
    campaign_criterion_service = client.get_service("CampaignCriterionService")
    
    # Create the operation
    operation = client.get_type("CampaignCriterionOperation")
    campaign_criterion = operation.create
    
    # Set the campaign to attach to
    campaign_criterion.campaign = client.get_service("CampaignService").campaign_path(CUSTOMER_ID, CAMPAIGN_ID)
    
    # Set the user list as the criterion (negative)
    campaign_criterion.user_list.user_list = client.get_service("UserListService").user_list_path(CUSTOMER_ID, USER_LIST_ID)
    
    # Make it NEGATIVE (Exclusion)
    campaign_criterion.negative = True
    
    print(f"--- Applying Exclusion ---")
    print(f"Campaign: {CAMPAIGN_ID}")
    print(f"Excluding User List: {USER_LIST_ID} (Purchasers)")
    
    try:
        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=CUSTOMER_ID,
            operations=[operation]
        )
        
        for result in response.results:
            print(f"SUCCESS: Applied negative criterion '{result.resource_name}'.")
            
    except GoogleAdsException as ex:
        print(f"Request failed with status '{ex.error.code().name}'")
        for error in ex.failure.errors:
            print(f"\tError: {error.message}")
            if "CRITERION_ALREADY_EXISTS" in error.message:
                print("\t-> Good news: This exclusion is already in place!")

if __name__ == "__main__":
    apply_exclusion()
