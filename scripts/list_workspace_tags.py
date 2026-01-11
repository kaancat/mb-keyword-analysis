import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def list_workspace_tags():
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
    
    print(f"Looking for workspace '{workspace_name}'...")
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
    print(f"Found workspace: {workspace_path}")
    
    # 2. List Tags
    print("Listing tags...")
    tags = service.list_tags(workspace_path)
    for tag in tags:
        print(f"Tag: {tag['name']} (ID: {tag['tag_id']}, Type: {tag['type']})")

if __name__ == "__main__":
    list_workspace_tags()
