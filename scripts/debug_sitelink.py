import os
import sys
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def debug_sitelink():
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
        
        print("--- SitelinkAsset ---")
        sitelink = client.get_type("SitelinkAsset")
        try:
            sitelink.final_urls.append("http://example.com")
            print("Success: sitelink.final_urls exists and is appendable.")
        except AttributeError:
            print("Failure: sitelink.final_urls does NOT exist.")
            
        print("\n--- Asset ---")
        asset = client.get_type("Asset")
        print("Asset fields:", dir(asset))
        try:
            asset.final_urls.append("http://example.com")
            print("Success: asset.final_urls exists and is appendable.")
        except AttributeError:
            print("Failure: asset.final_urls does NOT exist.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_sitelink()
