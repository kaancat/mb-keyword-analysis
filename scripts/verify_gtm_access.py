from backend.services.gtm_service import GTMService
import sys

def verify_gtm():
    print("--- Verifying GTM Access ---")
    try:
        gtm = GTMService()
        if not gtm.service:
            print("❌ Failed to initialize GTMService. Check your .env file.")
            return

        accounts = gtm.list_accounts()
        print(f"✅ Successfully connected to GTM API.")
        print(f"Found {len(accounts)} accounts.")
        
        if accounts:
            print(f"First account: {accounts[0]['name']} ({accounts[0]['path']})")
            
            containers = gtm.list_containers(accounts[0]['path'])
            print(f"Found {len(containers)} containers in first account.")
        else:
            print("No accounts found (but API connection seems to work).")

    except Exception as e:
        print(f"❌ Error verifying GTM access: {e}")

if __name__ == "__main__":
    verify_gtm()
