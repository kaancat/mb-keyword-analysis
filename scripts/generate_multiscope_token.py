import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_tokens():
    print("--- Generating Multi-Scope Refresh Token ---")
    
    # 1. Define Scopes (Ads + Sheets + Drive)
    scopes = [
        "https://www.googleapis.com/auth/adwords",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive" 
    ]
    
    # 2. Get Client Config
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("ERROR: Missing Client ID or Secret in .env")
        return

    # 3. Run OAuth Flow
    flow = InstalledAppFlow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=scopes
    )
    
    print("\nPlease click the link below to authorize the application:")
    print("Make sure to check the boxes for both Google Ads and Google Sheets/Drive access.\n")
    
    creds = flow.run_local_server(port=8080)
    
    print("\n--- AUTHORIZATION SUCCESSFUL ---")
    print(f"New Refresh Token: {creds.refresh_token}")
    print("\nACTION REQUIRED: Copy the token above and update your .env file:")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")

if __name__ == "__main__":
    generate_tokens()
