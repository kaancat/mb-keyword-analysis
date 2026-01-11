import sys
import os
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.services.gtm_service import GTMService

def main():
    service = GTMService()
    if not service.service:
        print("Failed to initialize GTM Service.")
        return

    # 1. Find Account and Container
    target_account_id = "6217370788"
    target_container_id = "177601436" # Public ID: GTM-PLX7TXQ9
    
    account_path = f"accounts/{target_account_id}"
    container_path = f"accounts/{target_account_id}/containers/{target_container_id}"
    
    print(f"Targeting Container: {container_path}")

    # 2. Create New Workspace
    # We create a new workspace to avoid conflicts in the Default Workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_name = f"Antigravity Fix {timestamp}"
    
    print(f"Creating new workspace: {workspace_name}...")
    workspace = service.create_workspace(container_path, workspace_name, "Fixing Meta Lead -> BookingConfirmed")
    
    if not workspace:
        print("Failed to create workspace. Exiting.")
        return
        
    workspace_path = workspace['path']
    workspace_id = workspace['workspace_id']
    print(f"Workspace created: {workspace_path}")

    # 3. Get Tag 40
    tag_id = "40"
    print(f"Fetching Tag {tag_id}...")
    tag = service.get_tag(workspace_path, tag_id)
    
    if not tag:
        print(f"Tag {tag_id} not found. Listing all tags to verify ID...")
        tags = service.list_tags(workspace_path)
        for t in tags:
            print(f" - {t['tag_id']}: {t['name']}")
        return

    print(f"Found Tag: {tag['name']} (Type: {tag['type']})")
    
    # 4. Update Tag
    # The user wants to change 'Lead' to 'BookingConfirmed' in the HTML
    # Check if it's a Custom HTML tag
    if tag['type'] == 'html':
        # Find the 'html' parameter
        html_content = ""
        for param in tag.get('parameter', []):
            if param['key'] == 'html':
                html_content = param['value']
                break
        
        if not html_content:
            print("Error: Could not find HTML content in tag.")
            return
            
        print("Current HTML Content Snippet:")
        print(html_content[:100] + "...")
        
        if "fbq('track', 'Lead'" in html_content:
            new_html = html_content.replace("fbq('track', 'Lead'", "fbq('track', 'BookingConfirmed'")
            print("Applying fix: Lead -> BookingConfirmed")
            
            # Update the parameter
            for param in tag['parameter']:
                if param['key'] == 'html':
                    param['value'] = new_html
            
            # Update the tag
            updated_tag = service.update_tag(tag['path'], tag)
            if updated_tag:
                print("Tag updated successfully.")
            else:
                print("Failed to update tag.")
                return
        elif "BookingConfirmed" in html_content:
            print("Tag already has 'BookingConfirmed'. No changes needed.")
        else:
            print("Warning: Could not find 'Lead' event in HTML. Please check manually.")
            print(html_content)
            return
    else:
        print(f"Unexpected tag type: {tag['type']}. Expected 'html'.")
        return

    # 5. Create Version
    print("Creating Version...")
    version_name = "Fix Meta event name Lead->BookingConfirmed"
    version = service.create_version(workspace_path, version_name, "Automated fix by Antigravity")
    
    if not version:
        print("Failed to create version.")
        return
        
    version_path = version['path']
    print(f"Version created: {version_path}")

    # 6. Publish Version
    print("Publishing Version...")
    published = service.publish_version(version_path)
    
    if published:
        print("SUCCESS: Version published.")
        print(f"Live Version: {published.get('containerVersion', {}).get('containerVersionId')}")
    else:
        print("Failed to publish version.")

if __name__ == "__main__":
    main()
