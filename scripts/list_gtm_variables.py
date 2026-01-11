import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def list_variables():
    service = GTMService()
    if not service.service:
        print("Failed to initialize GTM Service.")
        return

    account_id = '6217370788'
    container_id = '177601436'
    workspace_name = 'tracking-fix-2025-11-28'
    
    # 1. Find Workspace
    account_path = f"accounts/{account_id}"
    container_path = f"{account_path}/containers/{container_id}"
    
    workspaces = service.list_workspaces(container_path)
    target_workspace = None
    for ws in workspaces:
        if ws['name'] == workspace_name:
            target_workspace = ws
            break
            
    if not target_workspace:
        print(f"Workspace '{workspace_name}' not found.")
        return

    print(f"Listing variables for workspace: {target_workspace['name']}")
    
    try:
        response = service.service.accounts().containers().workspaces().variables().list(
            parent=target_workspace['path']
        ).execute()
        
        variables = response.get('variable', [])
        print(f"Found {len(variables)} variables.")
        
        for var in variables:
            print(f"Variable: {var['name']} (ID: {var['variableId']}, Type: {var['type']})")
            
    except Exception as e:
        print(f"Error listing variables: {e}")

if __name__ == "__main__":
    list_variables()
