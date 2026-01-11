"""
NMD Law Group - Tracking Configuration
======================================

Central configuration for all NMD tracking scripts.
Update the CONVERSION_ACTION_IDs after running create_nmd_conversion_action.py
"""

# Google Ads Configuration
NMD_GOOGLE_ADS = {
    "customer_id": "7562650658",
    "mcc_id": "8959543272",  # MondayBrew MCC
    # Conversion Action IDs - Created 2025-12-01
    "conversion_actions": {
        "lead_form": "7403121584",  # Lead Form Submission
        "qualified_lead": "7403121827",  # Qualified Lead (Offline)
        "phone_click": "7403027221",  # Phone Call Click
    },
    "default_currency": "DKK",
    "timezone": "Europe/Copenhagen",
}

# GTM Configuration
NMD_GTM = {
    "container_id": "GTM-KZXHBNVN",
    "container_name": "NMD Law Group",
}

# GA4 Configuration
NMD_GA4 = {
    "measurement_id": "G-GMJZFFYVF7",
    "api_secret": "",  # Get from GA4 Admin > Data Streams > Measurement Protocol
}

# GHL Configuration
NMD_GHL = {
    "location_id": "",  # NMD's GHL location ID
    "webhook_endpoints": {
        "form_submission": "/webhook/nmd-form-submission",
        "pipeline_change": "/webhook/nmd-pipeline-change",
    },
    # Pipeline stage mappings - customize based on NMD's actual pipeline
    "qualified_stages": [
        "qualified",
        "qualified lead",
        "consultation booked",
        "consultation completed",
        "won",
        "closed won",
        "client",
    ],
}

# Conversion Values (in DKK)
CONVERSION_VALUES = {
    "lead_form": 500,  # Default value for form submission
    "qualified_lead": 2000,  # Default value for qualified lead
    "phone_click": 300,  # Default value for phone click
    "consultation_booked": 1500,
    "consultation_completed": 3000,
    "client_won": 10000,  # Or use actual deal value
}

# n8n Configuration
N8N_CONFIG = {
    "base_url": "",  # e.g., "https://your-n8n.example.com"
    "webhook_path_form": "nmd-form-submission",
    "webhook_path_pipeline": "nmd-pipeline-change",
}


def get_full_webhook_url(webhook_type: str) -> str:
    """Get the full webhook URL for n8n."""
    base = N8N_CONFIG["base_url"].rstrip("/")
    if webhook_type == "form":
        return f"{base}/webhook/{N8N_CONFIG['webhook_path_form']}"
    elif webhook_type == "pipeline":
        return f"{base}/webhook/{N8N_CONFIG['webhook_path_pipeline']}"
    return ""


def get_conversion_action_resource(action_type: str) -> str:
    """Get the full resource name for a conversion action."""
    action_id = NMD_GOOGLE_ADS["conversion_actions"].get(action_type, "")
    if action_id:
        return (
            f"customers/{NMD_GOOGLE_ADS['customer_id']}/conversionActions/{action_id}"
        )
    return ""
