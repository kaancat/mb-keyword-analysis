import sys
import os

# Add the project root to the python path so we can import backend.services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def fix_variable():
    service = GTMService()
    if not service.service:
        print("Failed to initialize GTM Service.")
        return

    # 1. Find the correct workspace
    # We know the container ID from the browser URL: GTM-PLX7TXQ9 -> Container ID: 17760143
    # Account ID: 6217370788
    # Workspace Name: 'tracking-fix-2025-11-28'
    
    account_id = '6217370788'
    container_id = '177601436'
    workspace_name = 'tracking-fix-2025-11-28'
    
    # Construct paths
    account_path = f"accounts/{account_id}"
    container_path = f"{account_path}/containers/{container_id}"
    
    print(f"Looking for workspace '{workspace_name}' in {container_path}...")
    
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

    # 2. Find the variable 'CJS - Click IDs'
    print("Looking for variable 'CJS - Click IDs'...")
    try:
        response = service.service.accounts().containers().workspaces().variables().list(
            parent=workspace_path
        ).execute()
        
        variables = response.get('variable', [])
        target_variable = None
        for var in variables:
            if var['name'] == 'CJS - Click IDs':
                target_variable = var
                break
        
        if not target_variable:
            print("Variable 'CJS - Click IDs' not found.")
            return
            
        print(f"Found variable: {target_variable['variableId']}")
        
        # 3. Update the variable
        # The correct JS code
        correct_js = """function() {
  try {
    var ids = localStorage.getItem('kd_click_ids');
    return ids ? JSON.parse(ids) : undefined;
  } catch(e) {
    return undefined;
  }
}"""
        
        # Update the parameter list
        # Custom Javascript variables usually have a parameter with type 'template' and key 'javascript'
        
        variable_body = {
            "name": target_variable['name'],
            "type": "jsm", # Custom JavaScript type
            "parameter": [
                {
                    "type": "template",
                    "key": "javascript",
                    "value": correct_js
                }
            ]
        }
        
        print("Updating variable...")
        update_response = service.service.accounts().containers().workspaces().variables().update(
            path=target_variable['path'],
            body=variable_body
        ).execute()
        
        print("Variable updated successfully!")
        print(f"New Fingerprint: {update_response.get('fingerprint')}")
        
    except Exception as e:
        print(f"Error updating variable: {e}")

if __name__ == "__main__":
    fix_variable()
