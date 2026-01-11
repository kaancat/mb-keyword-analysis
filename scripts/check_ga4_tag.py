import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def check_ga4_tag():
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

    workspace_path = target_workspace['path']
    
    # 2. Get Tag 10
    try:
        tag = service.service.accounts().containers().workspaces().tags().get(
            path=f"{workspace_path}/tags/10"
        ).execute()
        
        print(f"Tag: {tag['name']} (ID: {tag['tagId']})")
        print("Parameters:")
        print(json.dumps(tag.get('parameter', []), indent=2))
        
    except Exception as e:
        print(f"Error getting tag: {e}")

if __name__ == "__main__":
    check_ga4_tag()
