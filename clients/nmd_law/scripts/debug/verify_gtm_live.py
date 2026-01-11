import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.services.gtm_service import GTMService

GTM_CONTAINER_PUBLIC_ID = "GTM-KZXHBNVN"

def verify_live_version():
    gtm = GTMService()
    accounts = gtm.list_accounts()
    container_path = None
    
    # Find container
    for account in accounts:
        containers = gtm.list_containers(account["path"])
        for c in containers:
            if c["public_id"] == GTM_CONTAINER_PUBLIC_ID:
                container_path = c["path"]
                break
        if container_path: break
    
    if not container_path:
        print("Container not found")
        return

    print(f"Container: {container_path}")
    
    # Get Live Version
    try:
        live_version = gtm.service.accounts().containers().versions().live().get(parent=container_path).execute()
        print(f"Live Version ID: {live_version['containerVersionId']}")
        
        # List Tags in Live Version
        tags = live_version.get("tag", [])
        print(f"\nTags in Live Version ({len(tags)}):")
        found_gclid = False
        for tag in tags:
            print(f"- {tag['name']} ({tag['type']})")
            if tag['name'] == "Custom HTML - Store GCLID":
                found_gclid = True
                
        if found_gclid:
            print("\n✅ 'Custom HTML - Store GCLID' is PUBLISHED and LIVE.")
        else:
            print("\n❌ 'Custom HTML - Store GCLID' is NOT in the live version.")
            
    except Exception as e:
        print(f"Error getting live version: {e}")

if __name__ == "__main__":
    verify_live_version()
