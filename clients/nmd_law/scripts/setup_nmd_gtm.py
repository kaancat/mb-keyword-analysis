"""
GTM Setup Script for NMD Law Group
===================================

This script configures GTM with:
1. Variables: GCLID capture, Data Layer variables
2. Triggers: Page view, Form submission, Phone click
3. Tags: GA4 config, GCLID storage, Form tracking, Phone tracking

Requirements:
- GTM Container: GTM-KZXHBNVN
- GA4 Measurement ID: G-GMJZFFYVF7
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv

load_dotenv()

from backend.services.gtm_service import GTMService

# NMD Law Group Configuration
GTM_CONTAINER_PUBLIC_ID = "GTM-KZXHBNVN"
GA4_MEASUREMENT_ID = "G-GMJZFFYVF7"
FB_PIXEL_ID = "1642362299753454"
GOOGLE_ADS_CONVERSION_ID = ""  # Will be set after creating conversion actions


def find_nmd_container(gtm_service):
    """Find NMD's GTM container path."""
    accounts = gtm_service.list_accounts()

    for account in accounts:
        containers = gtm_service.list_containers(account["path"])
        for container in containers:
            if container["public_id"] == GTM_CONTAINER_PUBLIC_ID:
                print(
                    f"Found container: {container['name']} ({container['public_id']})"
                )
                return container["path"]

    return None


def get_or_create_workspace(gtm_service, container_path: str):
    """Get default workspace or create a new one for tracking setup."""
    workspaces = gtm_service.list_workspaces(container_path)
    print(f"Available workspaces: {[ws['name'] for ws in workspaces]}")

    # 1. Look for specific workspace
    for ws in workspaces:
        if ws["name"] == "Tracking Setup - MondayBrew":
            print(f"Using existing workspace: {ws['name']}")
            return ws["path"]

    # 2. Create new workspace if not found
    # Note: GTM limits number of workspaces (usually 3). 
    # If we can't create, we must fall back to Default.
    if len(workspaces) < 3:
        new_ws = gtm_service.create_workspace(
            container_path,
            name="Tracking Setup - MondayBrew",
            description="Server-side tracking setup by MondayBrew",
        )
        if new_ws:
            print(f"Created workspace: {new_ws['name']}")
            return new_ws["path"]
    else:
        print("⚠️  Workspace limit reached. Falling back to existing workspace.")

    # 3. Fallback to Default
    for ws in workspaces:
        if ws["name"] == "Default Workspace":
            print(f"Using default workspace")
            return ws["path"]

    # 4. Fallback to first available
    if workspaces:
        print(f"Using first available workspace: {workspaces[0]['name']}")
        return workspaces[0]["path"]

    return None


def create_variables(gtm_service, workspace_path: str):
    """Create or retrieve necessary GTM variables."""
    variables = {}
    
    print("\nCreating/Retrieving variables...")
    
    # 1. Custom Variables
    existing_vars = gtm_service.list_variables(workspace_path)
    existing_vars_map = {v['name']: v for v in existing_vars}

    def ensure_variable(var_def):
        name = var_def["name"]
        if name in existing_vars_map:
            print(f"  ✅ Found existing: {name}")
            return existing_vars_map[name]
        else:
            result = gtm_service.create_variable(workspace_path, var_def)
            if result:
                print(f"  ✅ Created: {name}")
                return result
            return None

    # 1a. GCLID from URL
    variables["gclid_url"] = ensure_variable({
        "name": "URL - GCLID",
        "type": "u",
        "parameter": [
            {"type": "template", "key": "component", "value": "QUERY"},
            {"type": "template", "key": "queryKey", "value": "gclid"},
        ],
    })

    # 1b. FBCLID from URL
    variables["fbclid_url"] = ensure_variable({
        "name": "URL - FBCLID",
        "type": "u",
        "parameter": [
            {"type": "template", "key": "component", "value": "QUERY"},
            {"type": "template", "key": "queryKey", "value": "fbclid"},
        ],
    })

    # 2a. GCLID from Cookie
    variables["gclid_cookie"] = ensure_variable({
        "name": "Cookie - GCLID",
        "type": "k",
        "parameter": [{"type": "template", "key": "name", "value": "_gclid"}],
    })

    # 2b. FBCLID from Cookie
    variables["fbclid_cookie"] = ensure_variable({
        "name": "Cookie - FBCLID",
        "type": "k",
        "parameter": [{"type": "template", "key": "name", "value": "_fbclid"}],
    })
    
    # 3. UTM Parameters
    variables["utm_source"] = ensure_variable({
        "name": "URL - UTM Source",
        "type": "u",
        "parameter": [
            {"type": "template", "key": "component", "value": "QUERY"},
            {"type": "template", "key": "queryKey", "value": "utm_source"},
        ],
    })

    variables["utm_medium"] = ensure_variable({
        "name": "URL - UTM Medium",
        "type": "u",
        "parameter": [
            {"type": "template", "key": "component", "value": "QUERY"},
            {"type": "template", "key": "queryKey", "value": "utm_medium"},
        ],
    })

    variables["utm_campaign"] = ensure_variable({
        "name": "URL - UTM Campaign",
        "type": "u",
        "parameter": [
            {"type": "template", "key": "component", "value": "QUERY"},
            {"type": "template", "key": "queryKey", "value": "utm_campaign"},
        ],
    })

    # 4. Built-In Variables
    print("\nEnabling Built-In Variables...")
    existing_built_ins = gtm_service.list_built_in_variables(workspace_path)
    existing_built_ins_types = {v['type'] for v in existing_built_ins}
    
    built_ins_to_enable = [
        "formId", 
        "clickUrl", 
        "pageUrl",
        "pagePath"
    ]
    
    for var_type in built_ins_to_enable:
        if var_type in existing_built_ins_types:
            print(f"  ✅ Already enabled: {var_type}")
        else:
            result = gtm_service.enable_built_in_variable(workspace_path, var_type)
            if result:
                print(f"  ✅ Enabled: {var_type}")
    
    # Note: Built-in variables are referenced by their standard names in GTM UI (e.g. "Form ID", "Click URL")
    # We don't need to return them in the 'variables' dict for tag creation if we use {{Form ID}} directly.
    
    return variables


def create_triggers(gtm_service, workspace_path: str):
    """Create or retrieve necessary GTM triggers."""
    triggers = {}
    
    print("\nCreating/Retrieving triggers...")
    
    # Get existing triggers
    existing_triggers = gtm_service.list_triggers(workspace_path)
    existing_triggers_map = {t['name']: t for t in existing_triggers}

    # 1. All Pages trigger
    if "All Pages" in existing_triggers_map:
        triggers["all_pages"] = existing_triggers_map["All Pages"]
        # Map triggerId for compatibility
        triggers["all_pages"]["triggerId"] = existing_triggers_map["All Pages"]["trigger_id"]
        print(f"  ✅ Found existing: All Pages")
    else:
        all_pages_trigger = {"name": "All Pages", "type": "pageview"}
        result = gtm_service.create_trigger(workspace_path, all_pages_trigger)
        if result:
            triggers["all_pages"] = result
            print(f"  ✅ Created: All Pages")

    # 2. Phone Click trigger (tel: links)
    if "Click - Phone Number" in existing_triggers_map:
        triggers["phone_click"] = existing_triggers_map["Click - Phone Number"]
        triggers["phone_click"]["triggerId"] = existing_triggers_map["Click - Phone Number"]["trigger_id"]
        print(f"  ✅ Found existing: Click - Phone Number")
    else:
        phone_click_trigger = {
            "name": "Click - Phone Number",
            "type": "linkClick",
            "parameter": [
                {"type": "boolean", "key": "waitForTags", "value": "false"},
                {"type": "boolean", "key": "checkValidation", "value": "true"},
                {"type": "boolean", "key": "waitForTagsTimeout", "value": "2000"},
            ],
            "filter": [
                {
                    "type": "contains",
                    "parameter": [
                        {"type": "template", "key": "arg0", "value": "{{Click URL}}"},
                        {"type": "template", "key": "arg1", "value": "tel:"},
                    ],
                }
            ],
        }
        result = gtm_service.create_trigger(workspace_path, phone_click_trigger)
        if result:
            triggers["phone_click"] = result
            print(f"  ✅ Created: Click - Phone Number")

    # 3. Form Submission trigger (for GHL forms)
    if "Form Submission - All Forms" in existing_triggers_map:
        triggers["form_submit"] = existing_triggers_map["Form Submission - All Forms"]
        triggers["form_submit"]["triggerId"] = existing_triggers_map["Form Submission - All Forms"]["trigger_id"]
        print(f"  ✅ Found existing: Form Submission - All Forms")
    else:
        form_submit_trigger = {
            "name": "Form Submission - All Forms",
            "type": "formSubmission",
            "parameter": [
                {"type": "boolean", "key": "waitForTags", "value": "true"},
                {"type": "boolean", "key": "checkValidation", "value": "true"},
                {"type": "template", "key": "waitForTagsTimeout", "value": "2000"},
            ],
        }
        result = gtm_service.create_trigger(workspace_path, form_submit_trigger)
        if result:
            triggers["form_submit"] = result
            print(f"  ✅ Created: Form Submission - All Forms")

    # 4. Window Loaded (for GCLID storage)
    if "Window Loaded" in existing_triggers_map:
        triggers["window_loaded"] = existing_triggers_map["Window Loaded"]
        triggers["window_loaded"]["triggerId"] = existing_triggers_map["Window Loaded"]["trigger_id"]
        print(f"  ✅ Found existing: Window Loaded")
    else:
        window_loaded_trigger = {"name": "Window Loaded", "type": "windowLoaded"}
        result = gtm_service.create_trigger(workspace_path, window_loaded_trigger)
        if result:
            triggers["window_loaded"] = result
            print(f"  ✅ Created: Window Loaded")

    return triggers


def create_tags(gtm_service, workspace_path: str, triggers: dict):
    """Create or update necessary GTM tags."""
    tags = {}
    
    print("\nCreating/Updating tags...")
    
    # Get existing tags to check for updates
    existing_tags = gtm_service.list_tags(workspace_path)
    existing_tags_map = {t['name']: t for t in existing_tags}

    # Get trigger IDs
    all_pages_id = triggers.get("all_pages", {}).get("triggerId")
    phone_click_id = triggers.get("phone_click", {}).get("triggerId")
    form_submit_id = triggers.get("form_submit", {}).get("triggerId")
    window_loaded_id = triggers.get("window_loaded", {}).get("triggerId")

    # 1. GA4 Configuration Tag
    if all_pages_id:
        ga4_config_tag = {
            "name": "GA4 - Configuration",
            "type": "gaawc",  # GA4 Configuration
            "parameter": [
                {
                    "type": "template",
                    "key": "measurementId",
                    "value": GA4_MEASUREMENT_ID,
                },
                {"type": "boolean", "key": "sendPageView", "value": "true"},
            ],
            "firingTriggerId": [all_pages_id],
        }
        
        if "GA4 - Configuration" in existing_tags_map:
            tag_path = existing_tags_map["GA4 - Configuration"]["path"]
            result = gtm_service.update_tag(tag_path, ga4_config_tag)
            if result:
                tags["ga4_config"] = result
                print(f"  ✅ Updated: GA4 - Configuration")
        else:
            result = gtm_service.create_tag(workspace_path, ga4_config_tag)
            if result:
                tags["ga4_config"] = result
                print(f"  ✅ Created: GA4 - Configuration")

    # 1b. Facebook Pixel Base Code
    if all_pages_id:
        fb_pixel_tag = {
            "name": "Facebook Pixel - Base Code",
            "type": "html",
            "parameter": [
                {
                    "type": "template",
                    "key": "html",
                    "value": f"""<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{FB_PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={FB_PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
<!-- End Facebook Pixel Code -->""",
                }
            ],
            "firingTriggerId": [all_pages_id],
        }
        
        if "Facebook Pixel - Base Code" in existing_tags_map:
            tag_path = existing_tags_map["Facebook Pixel - Base Code"]["path"]
            result = gtm_service.update_tag(tag_path, fb_pixel_tag)
            if result:
                tags["fb_pixel"] = result
                print(f"  ✅ Updated: Facebook Pixel - Base Code")
        else:
            if result:
                tags["fb_pixel"] = result
                print(f"  ✅ Created: Facebook Pixel - Base Code")

    # 1c. Facebook Pixel - Lead Event
    if form_submit_id:
        fb_lead_tag = {
            "name": "Facebook Pixel - Lead",
            "type": "html",
            "parameter": [
                {
                    "type": "template",
                    "key": "html",
                    "value": f"""<script>
  fbq('track', 'Lead');
</script>""",
                }
            ],
            "firingTriggerId": [form_submit_id],
            "tagFiringOption": "oncePerEvent",
        }
        
        if "Facebook Pixel - Lead" in existing_tags_map:
            tag_path = existing_tags_map["Facebook Pixel - Lead"]["path"]
            result = gtm_service.update_tag(tag_path, fb_lead_tag)
            if result:
                tags["fb_lead"] = result
                print(f"  ✅ Updated: Facebook Pixel - Lead")
        else:
            result = gtm_service.create_tag(workspace_path, fb_lead_tag)
            if result:
                tags["fb_lead"] = result
                print(f"  ✅ Created: Facebook Pixel - Lead")

    # 2. GCLID Storage Tag (Custom HTML)
    if window_loaded_id:
        gclid_storage_tag = {
            "name": "Custom HTML - Store GCLID",
            "type": "html",
            "parameter": [
                {
                    "type": "template",
                    "key": "html",
                    "value": """<script>
(function() {
  // Helper to set cookie
  function setCookie(name, value, days) {
    var expires = "";
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
  }

  // Helper to get cookie
  function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
  }

  // 1. Capture IDs from URL
  var urlParams = new URLSearchParams(window.location.search);
  var gclid = urlParams.get('gclid');
  var fbclid = urlParams.get('fbclid');
  
  console.log('MondayBrew Tracking: Checking for GCLID...', { gclid: gclid, fbclid: fbclid });

  // 2. Store GCLID
  if (gclid) {
    setCookie('_gclid', gclid, 90);
    try {
      localStorage.setItem('_gclid', gclid);
      localStorage.setItem('_gclid_timestamp', Date.now().toString());
      console.log('MondayBrew Tracking: Saved GCLID to cookie/localstorage');
    } catch(e) {
      console.error('MondayBrew Tracking: Failed to save GCLID', e);
    }
  }

  // 3. Store FBCLID
  if (fbclid) {
    setCookie('_fbclid', fbclid, 90);
    try {
      localStorage.setItem('_fbclid', fbclid);
    } catch(e) {}
  }

  // 4. Retrieve stored values (if not in URL)
  if (!gclid) {
    gclid = getCookie('_gclid') || localStorage.getItem('_gclid');
    console.log('MondayBrew Tracking: Retrieved GCLID from storage', gclid);
  }
  if (!fbclid) {
    fbclid = getCookie('_fbclid') || localStorage.getItem('_fbclid');
  }

  // 5. Populate hidden fields (if any exist on parent page)
  if (gclid) {
    var inputs = document.querySelectorAll('input[name="gclid"], input[name="GCLID"]');
    inputs.forEach(function(el) { el.value = gclid; });
    console.log('MondayBrew Tracking: Populated ' + inputs.length + ' hidden fields');
  }
  if (fbclid) {
    document.querySelectorAll('input[name="fbclid"], input[name="FBCLID"]').forEach(function(el) { el.value = fbclid; });
  }

  // 6. Listen for requests from GHL iframe
  window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'REQUEST_GCLID') {
      var response = {
        type: 'GCLID_VALUE',
        gclid: gclid || '',
        fbclid: fbclid || ''
      };
      if (event.source) {
        event.source.postMessage(response, '*');
        console.log('MondayBrew Tracking: Sent GCLID to iframe');
      }
    }
  });

})();
</script>""",
                }
            ],
            "firingTriggerId": [all_pages_id],
        }
        
        if "Custom HTML - Store GCLID" in existing_tags_map:
            tag_path = existing_tags_map["Custom HTML - Store GCLID"]["path"]
            result = gtm_service.update_tag(tag_path, gclid_storage_tag)
            if result:
                tags["gclid_storage"] = result
                print(f"  ✅ Updated: Custom HTML - Store GCLID")
        else:
            result = gtm_service.create_tag(workspace_path, gclid_storage_tag)
            if result:
                tags["gclid_storage"] = result
                print(f"  ✅ Created: Custom HTML - Store GCLID")

    # 3. GA4 Event - Form Submission
    if form_submit_id:
        ga4_form_event = {
            "name": "GA4 Event - Form Submission",
            "type": "gaawe",  # GA4 Event
            "parameter": [
                {"type": "template", "key": "eventName", "value": "generate_lead"},
                {
                    "type": "tagReference",
                    "key": "measurementId",
                    "value": "GA4 - Configuration",
                },
                {
                    "type": "list",
                    "key": "eventParameters",
                    "list": [
                        {
                            "type": "map",
                            "map": [
                                {"type": "template", "key": "name", "value": "form_id"},
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Form ID}}",
                                },
                            ],
                        },
                        {
                            "type": "map",
                            "map": [
                                {
                                    "type": "template",
                                    "key": "name",
                                    "value": "page_url",
                                },
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Page URL}}",
                                },
                            ],
                        },
                        {
                            "type": "map",
                            "map": [
                                {"type": "template", "key": "name", "value": "gclid"},
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Cookie - GCLID}}",
                                },
                            ],
                        },
                    ],
                },
            ],
            "firingTriggerId": [form_submit_id],
        }
        result = gtm_service.create_tag(workspace_path, ga4_form_event)
        if result:
            tags["ga4_form_event"] = result
            print(f"  ✅ Created: GA4 Event - Form Submission")

    # 4. GA4 Event - Phone Click
    if phone_click_id:
        ga4_phone_event = {
            "name": "GA4 Event - Phone Click",
            "type": "gaawe",
            "parameter": [
                {"type": "template", "key": "eventName", "value": "phone_click"},
                {
                    "type": "tagReference",
                    "key": "measurementId",
                    "value": "GA4 - Configuration",
                },
                {
                    "type": "list",
                    "key": "eventParameters",
                    "list": [
                        {
                            "type": "map",
                            "map": [
                                {
                                    "type": "template",
                                    "key": "name",
                                    "value": "phone_number",
                                },
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Click URL}}",
                                },
                            ],
                        },
                        {
                            "type": "map",
                            "map": [
                                {
                                    "type": "template",
                                    "key": "name",
                                    "value": "page_url",
                                },
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Page URL}}",
                                },
                            ],
                        },
                        {
                            "type": "map",
                            "map": [
                                {"type": "template", "key": "name", "value": "gclid"},
                                {
                                    "type": "template",
                                    "key": "value",
                                    "value": "{{Cookie - GCLID}}",
                                },
                            ],
                        },
                    ],
                },
            ],
            "firingTriggerId": [phone_click_id],
        }
        result = gtm_service.create_tag(workspace_path, ga4_phone_event)
        if result:
            tags["ga4_phone_event"] = result
            print(f"  ✅ Created: GA4 Event - Phone Click")

    return tags


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Set up GTM for NMD Law Group")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List current config without making changes",
    )
    parser.add_argument(
        "--publish", action="store_true", help="Publish changes after setup"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("GTM Setup for NMD Law Group")
    print(f"Container: {GTM_CONTAINER_PUBLIC_ID}")
    print(f"GA4: {GA4_MEASUREMENT_ID}")
    print("=" * 60)

    gtm_service = GTMService()

    if not gtm_service.service:
        print("❌ Failed to initialize GTM service. Check credentials.")
        return

    # Find container
    container_path = find_nmd_container(gtm_service)
    if not container_path:
        print(f"❌ Container {GTM_CONTAINER_PUBLIC_ID} not found")
        return

    print(f"Container path: {container_path}")

    # Get workspace
    workspace_path = get_or_create_workspace(gtm_service, container_path)
    if not workspace_path:
        print("❌ Could not get/create workspace")
        return

    print(f"Workspace path: {workspace_path}")

    if args.dry_run:
        print("\n[DRY RUN] Current configuration:")
        tags = gtm_service.list_tags(workspace_path)
        print(f"  Existing tags: {len(tags)}")
        for tag in tags:
            print(f"    - {tag['name']} ({tag['type']})")
        return

    # Create variables
    variables = create_variables(gtm_service, workspace_path)

    # Create triggers
    triggers = create_triggers(gtm_service, workspace_path)

    # Create tags
    tags = create_tags(gtm_service, workspace_path, triggers)

    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print(f"Variables created: {len(variables)}")
    print(f"Triggers created: {len(triggers)}")
    print(f"Tags created: {len(tags)}")

    if args.publish:
        print("\nPublishing changes...")
        version = gtm_service.create_version(
            workspace_path,
            name="MondayBrew Tracking Setup",
            notes="Server-side tracking configuration",
        )
        if version:
            gtm_service.publish_version(version.get("path", ""))
            print("✅ Published!")
    else:
        print("\n⚠️  Changes are saved but NOT published.")
        print("    Run with --publish to publish, or publish manually in GTM UI.")
        print(
            "    Review changes in GTM before publishing: https://tagmanager.google.com"
        )


if __name__ == "__main__":
    main()
