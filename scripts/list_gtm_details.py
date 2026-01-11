import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def list_all():
    service = GTMService()
    if not service.service:
        print("Failed to initialize GTM Service.")
        return

    print("--- Listing All Accounts ---")
    accounts = service.list_accounts()
    for acc in accounts:
        print(f"Account: {acc['name']} (ID: {acc['account_id']}, Path: {acc['path']})")
        
        containers = service.list_containers(acc['path'])
        for cont in containers:
            print(f"  - Container: {cont['name']} (ID: {cont['container_id']}, Public ID: {cont['public_id']}, Path: {cont['path']})")
            
            # Check workspaces for this container
            workspaces = service.list_workspaces(cont['path'])
            for ws in workspaces:
                print(f"    - Workspace: {ws['name']} (ID: {ws['workspace_id']})")

if __name__ == "__main__":
    list_all()
