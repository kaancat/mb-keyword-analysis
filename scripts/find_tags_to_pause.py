import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def find_tags():
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

    print(f"Found workspace: {target_workspace['name']} ({target_workspace['path']})")
    
    # 2. List Tags
    tags = service.list_tags(target_workspace['path'])
    target_ids = ['10', '40']
    
    for tag_id in target_ids:
        try:
            tag = service.service.accounts().containers().workspaces().tags().get(
                path=f"{target_workspace['path']}/tags/{tag_id}"
            ).execute()
            print(f"\n--- TAG DETAILS FOR ID {tag['tagId']} ({tag['name']}) ---")
            print(tag)
            print("--------------------------------------------------\n")
        except Exception as e:
            print(f"Error fetching tag {tag_id}: {e}")

if __name__ == "__main__":
    find_tags()
