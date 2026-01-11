import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def cleanup_tags():
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
    
    # Tags to disable
    tags_to_disable = ['18', '21']
    
    for tag_id in tags_to_disable:
        try:
            print(f"Retrieving tag ID {tag_id}...")
            tag = service.service.accounts().containers().workspaces().tags().get(
                path=f"{workspace_path}/tags/{tag_id}"
            ).execute()
            
            print(f"Disabling tag: {tag['name']}")
            
            # Remove firing triggers
            if 'firingTriggerId' in tag:
                print(f"Removing triggers: {tag['firingTriggerId']}")
                tag.pop('firingTriggerId')
                
                service.service.accounts().containers().workspaces().tags().update(
                    path=tag['path'],
                    body=tag
                ).execute()
                print("Tag disabled (triggers removed).")
            else:
                print("Tag has no firing triggers.")
                
        except Exception as e:
            print(f"Error processing tag {tag_id}: {e}")

if __name__ == "__main__":
    cleanup_tags()
