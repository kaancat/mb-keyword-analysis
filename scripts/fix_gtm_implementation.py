import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.gtm_service import GTMService

def fix_implementation():
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

    # 2. Create/Update Variables
    
    # Helper to create/update variable
    def ensure_variable(name, js_code):
        print(f"Ensuring variable '{name}' exists...")
        # Check if exists
        response = service.service.accounts().containers().workspaces().variables().list(
            parent=workspace_path
        ).execute()
        
        existing = None
        for var in response.get('variable', []):
            if var['name'] == name:
                existing = var
                break
        
        variable_body = {
            "name": name,
            "type": "jsm",
            "parameter": [
                {
                    "type": "template",
                    "key": "javascript",
                    "value": js_code
                }
            ]
        }
        
        if existing:
            print(f"Updating existing variable '{name}'...")
            return service.service.accounts().containers().workspaces().variables().update(
                path=existing['path'],
                body=variable_body
            ).execute()
        else:
            print(f"Creating new variable '{name}'...")
            return service.service.accounts().containers().workspaces().variables().create(
                parent=workspace_path,
                body=variable_body
            ).execute()

    # CJS - gclid
    js_gclid = """function() {
  try {
    var ids = JSON.parse(localStorage.getItem('kd_click_ids') || '{}');
    return ids.gclid;
  } catch(e) { return undefined; }
}"""
    ensure_variable("CJS - gclid", js_gclid)

    # CJS - fbclid
    js_fbclid = """function() {
  try {
    var ids = JSON.parse(localStorage.getItem('kd_click_ids') || '{}');
    return ids.fbclid;
  } catch(e) { return undefined; }
}"""
    ensure_variable("CJS - fbclid", js_fbclid)


    # 3. Update GA4 Tag
    print("Updating GA4 Tag...")
    tags_response = service.service.accounts().containers().workspaces().tags().list(
        parent=workspace_path
    ).execute()
    
    ga4_tag = None
    meta_tag = None
    
    for tag in tags_response.get('tag', []):
        if tag['tagId'] == '10': # GA4 - Event - booking_success
            ga4_tag = tag
        elif tag['tagId'] == '40': # Meta - Booking
            meta_tag = tag
            
    if ga4_tag:
        print(f"Found GA4 Tag: {ga4_tag['name']} (ID: {ga4_tag['tagId']})")
        
        # The tag uses 'eventSettingsTable' for parameters, not 'eventParameter'
        # Structure:
        # eventSettingsTable: [
        #   { map: [ {key: parameter, value: gclid}, {key: parameterValue, value: {{CJS - Click IDs}}.gclid} ] },
        #   ...
        # ]
        
        new_settings = [
            {
                "type": "map",
                "map": [
                    {"type": "template", "key": "parameter", "value": "gclid"},
                    {"type": "template", "key": "parameterValue", "value": "{{CJS - gclid}}"}
                ]
            },
            {
                "type": "map",
                "map": [
                    {"type": "template", "key": "parameter", "value": "fbclid"},
                    {"type": "template", "key": "parameterValue", "value": "{{CJS - fbclid}}"}
                ]
            }
        ]
        
        updated_tag_params = []
        settings_found = False
        
        for param in ga4_tag.get('parameter', []):
            if param['key'] == 'eventSettingsTable':
                settings_found = True
                updated_tag_params.append({
                    "key": "eventSettingsTable",
                    "type": "list",
                    "list": new_settings
                })
            else:
                updated_tag_params.append(param)
        
        if not settings_found:
             updated_tag_params.append({
                    "key": "eventSettingsTable",
                    "type": "list",
                    "list": new_settings
                })
        
        ga4_tag['parameter'] = updated_tag_params
        
        print("Sending update for GA4 Tag...")
        service.service.accounts().containers().workspaces().tags().update(
            path=ga4_tag['path'],
            body=ga4_tag
        ).execute()
        print("GA4 Tag updated.")
    else:
        print("GA4 Tag (ID 10) not found.")

    # 4. Update Meta Tag
    if meta_tag:
        print(f"Found Meta Tag: {meta_tag['name']} (ID: {meta_tag['tagId']})")
        # Custom HTML tag has a 'html' parameter
        
        new_html = """<script>
  fbq('track', 'Purchase', {
    value: 0,
    currency: 'DKK',
    gclid: {{CJS - gclid}},
    fbclid: {{CJS - fbclid}}
  });
</script>"""

        updated_meta_params = []
        for param in meta_tag.get('parameter', []):
            if param['key'] == 'html':
                updated_meta_params.append({
                    "type": "template",
                    "key": "html",
                    "value": new_html
                })
            else:
                updated_meta_params.append(param)
                
        meta_tag['parameter'] = updated_meta_params
        
        print("Sending update for Meta Tag...")
        service.service.accounts().containers().workspaces().tags().update(
            path=meta_tag['path'],
            body=meta_tag
        ).execute()
        print("Meta Tag updated.")
    else:
        print("Meta Tag not found.")

if __name__ == "__main__":
    fix_implementation()
