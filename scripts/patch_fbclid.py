import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def patch_fbclid_variable():
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
    
    # 2. Find Variable
    response = service.service.accounts().containers().workspaces().variables().list(
        parent=workspace_path
    ).execute()
    
    target_var = None
    for var in response.get('variable', []):
        if var['name'] == 'CJS - fbclid':
            target_var = var
            break
            
    if target_var:
        print(f"Updating variable: {target_var['name']} (ID: {target_var['variableId']})")
        
        # Robust JS to clean the value
        clean_js = """function() {
  try {
    var ids = JSON.parse(localStorage.getItem('kd_click_ids') || '{}');
    var val = ids.fbclid;
    if (typeof val === 'string' && val.indexOf('http') > -1) {
        return val.split('http')[0];
    }
    return val;
  } catch(e) { return undefined; }
}"""
        
        target_var['parameter'] = [
            {
                "type": "template",
                "key": "javascript",
                "value": clean_js
            }
        ]
        
        service.service.accounts().containers().workspaces().variables().update(
            path=target_var['path'],
            body=target_var
        ).execute()
        print("Variable updated.")
    else:
        print("Variable not found.")

if __name__ == "__main__":
    patch_fbclid_variable()
