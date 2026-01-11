
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
load_dotenv()

from backend.services.gtm_service import GTMService

def main():
    gtm_service = GTMService()
    if not gtm_service.service:
        print("Failed to init GTM Service")
        return

    # Hardcoded for speed based on previous logs
    # Account: 6326356251
    # Container: 236525009
    # Workspace: We need to find "Tracking Setup - MondayBrew"
    
    container_path = "accounts/6326356251/containers/236525009"
    workspaces = gtm_service.list_workspaces(container_path)
    
    target_ws = None
    for ws in workspaces:
        if ws["name"] == "Tracking Setup - MondayBrew":
            target_ws = ws
            break
            
    if not target_ws:
        print("Could not find 'Tracking Setup - MondayBrew' workspace")
        # Fallback to default or first
        target_ws = workspaces[0]
        print(f"Falling back to: {target_ws['name']}")
        
    ws_path = target_ws["path"]
    print(f"Inspecting Workspace: {target_ws['name']} ({ws_path})")
    
    print("\n--- User-Defined Variables ---")
    vars = gtm_service.list_variables(ws_path)
    for v in vars:
        print(f"Name: '{v['name']}' | Type: {v['type']} | ID: {v['variable_id']}")
        
    print("\n--- Built-In Variables ---")
    built_ins = gtm_service.list_built_in_variables(ws_path)
    for b in built_ins:
        print(f"Name: '{b['name']}' | Type: {b['type']}")

if __name__ == "__main__":
    main()
