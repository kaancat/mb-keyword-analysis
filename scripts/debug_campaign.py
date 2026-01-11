import os
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def debug_campaign():
    # Load .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    
    try:
        client = GoogleAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True
        })
        
        print("--- Campaign ---")
        campaign = client.get_type("Campaign")
        print("Campaign fields:", dir(campaign))
        
        if hasattr(campaign, 'contains_eu_political_advertising'):
            print("Field 'contains_eu_political_advertising' exists.")
            print(f"Type: {type(campaign.contains_eu_political_advertising)}")
            
            # Print Enum members
            # We need to find the Enum class. It's likely in client.enums.
            # But the type printed was <enum 'EuPoliticalAdvertisingStatus'> which might be internal.
            # Let's try to access it via client.enums.
            
            # Search for the enum in client.enums
            found = False
            for name in dir(client.enums):
                if 'Political' in name:
                    print(f"Found potential enum: {name}")
                    enum_cls = getattr(client.enums, name)
                    print(f"Members: {dir(enum_cls)}")
                    # Try to print members
                    try:
                        for member in enum_cls:
                            print(f"  {member.name}: {member.value}")
                    except:
                        pass
                    found = True
            
            if not found:
                print("Could not find Enum in client.enums. Trying to inspect the field type directly.")
                # It's hard to inspect the type directly from the instance field if it's a primitive wrapper.
                # But let's try.

        else:
            print("Field 'contains_eu_political_advertising' does NOT exist.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_campaign()
