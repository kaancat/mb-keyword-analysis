import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(Path.home() / ".mondaybrew" / ".env")

# The "Master" scopes we need for the Agency OS
SCOPES = [
    "https://www.googleapis.com/auth/adwords",  # Google Ads
    "https://www.googleapis.com/auth/analytics.readonly",  # GA4 (Read Only)
    "https://www.googleapis.com/auth/analytics.edit",  # GA4 (Edit Access)
    "https://www.googleapis.com/auth/webmasters.readonly",  # Search Console (Read Only)
    "https://www.googleapis.com/auth/tagmanager.edit.containers",  # Google Tag Manager (Write Access)
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",  # Google Tag Manager (Manage Versions)
    "https://www.googleapis.com/auth/tagmanager.publish",  # Google Tag Manager (Publish Access)
    "https://www.googleapis.com/auth/spreadsheets",  # Google Sheets (Read/Write)
    "https://www.googleapis.com/auth/drive",  # Google Drive (for Sheets creation)
]


def get_refresh_token():
    print("--- Master Key Generator ---")
    print("This script will generate a Refresh Token with access to:")
    print("1. Google Ads")
    print("2. Google Analytics 4")
    print("3. Google Search Console")
    print("4. Google Tag Manager")
    print("\n")

    # Try to load from env first
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

    # Fallback to input if not found
    if not client_id:
        client_id = input("Enter your OAuth Client ID: ").strip()
    if not client_secret:
        client_secret = input("Enter your OAuth Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Secret are required. Check your .env file.")
        return

    # Create the flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        SCOPES,
    )

    # Run the local server flow
    print("\nLaunching browser... Please login with your AGENCY ADMIN email.")
    creds = flow.run_local_server(port=0)

    print("\n--- SUCCESS! ---")
    print(
        "Here is your MASTER REFRESH TOKEN. Save this in your .env file as GOOGLE_ADS_REFRESH_TOKEN"
    )
    print("-" * 60)
    print(creds.refresh_token)
    print("-" * 60)


if __name__ == "__main__":
    # Install requirement if needed: pip install google-auth-oauthlib
    get_refresh_token()
