import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def apply_changes():
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
    print(f"Target Workspace: {workspace_path}")

    # --- 1. Pause Legacy Tags (18, 21) ---
    tags_to_pause = ['18', '21']
    for tag_id in tags_to_pause:
        try:
            print(f"Processing Tag ID {tag_id}...")
            tag = service.service.accounts().containers().workspaces().tags().get(
                path=f"{workspace_path}/tags/{tag_id}"
            ).execute()
            
            if 'firingTriggerId' in tag:
                print(f"  - Pausing tag: {tag['name']}")
                tag.pop('firingTriggerId')
                service.service.accounts().containers().workspaces().tags().update(
                    path=tag['path'],
                    body=tag
                ).execute()
                print("  - Tag paused.")
            else:
                print(f"  - Tag {tag['name']} is already paused (no firing triggers).")
                
        except Exception as e:
            print(f"Error pausing tag {tag_id}: {e}")

    # --- 2. Update Meta Tag (40) ---
    try:
        print("Processing Meta Tag (ID 40)...")
        tag_40 = service.service.accounts().containers().workspaces().tags().get(
            path=f"{workspace_path}/tags/40"
        ).execute()
        
        updated = False
        for param in tag_40.get('parameter', []):
            if param['key'] == 'html':
                current_html = param['value']
                if 'Purchase' in current_html:
                    print("  - Replacing 'Purchase' with 'Lead' in HTML...")
                    new_html = current_html.replace("'Purchase'", "'Lead'")
                    param['value'] = new_html
                    updated = True
                elif 'Lead' in current_html:
                    print("  - Tag already uses 'Lead'.")
                else:
                    print("  - Warning: Could not find 'Purchase' event in HTML.")
        
        if updated:
            service.service.accounts().containers().workspaces().tags().update(
                path=tag_40['path'],
                body=tag_40
            ).execute()
            print("  - Meta Tag updated successfully.")
            
            # Verify the update
            print("  - Verifying update persistence...")
            verified_tag = service.service.accounts().containers().workspaces().tags().get(
                path=f"{workspace_path}/tags/40"
            ).execute()
            
            verified_html = ""
            for param in verified_tag.get('parameter', []):
                if param['key'] == 'html':
                    verified_html = param['value']
            
            if "'Lead'" in verified_html and "'Purchase'" not in verified_html:
                print("  - SUCCESS: Meta tag verified as 'Lead'.")
            else:
                print(f"  - FAILURE: Meta tag verification failed. HTML content: {verified_html}")
            
    except Exception as e:
        print(f"Error updating Meta Tag: {e}")

    # --- 3. Verify GA4 Tag (10) ---
    try:
        print("Verifying GA4 Tag (ID 10)...")
        tag_10 = service.service.accounts().containers().workspaces().tags().get(
            path=f"{workspace_path}/tags/10"
        ).execute()
        
        has_gclid = False
        has_fbclid = False
        
        for param in tag_10.get('parameter', []):
            if param['key'] == 'eventSettingsTable':
                for item in param.get('list', []):
                    map_list = item.get('map', [])
                    key = None
                    val = None
                    for m in map_list:
                        if m['key'] == 'parameter':
                            key = m['value']
                        if m['key'] == 'parameterValue':
                            val = m['value']
                    
                    if key == 'gclid' and val == '{{CJS - gclid}}':
                        has_gclid = True
                    if key == 'fbclid' and val == '{{CJS - fbclid}}':
                        has_fbclid = True
        
        if has_gclid and has_fbclid:
            print("  - GA4 Tag verified: Contains gclid and fbclid CJS variables.")
        else:
            print(f"  - WARNING: GA4 Tag missing parameters. GCLID: {has_gclid}, FBCLID: {has_fbclid}")
            
    except Exception as e:
        print(f"Error verifying GA4 Tag: {e}")

if __name__ == "__main__":
    apply_changes()
