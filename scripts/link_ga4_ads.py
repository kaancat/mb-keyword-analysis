import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.services.ga4_service import GA4Service
from backend.services.ads_connector import AdsConnector

def main():
    # Configuration
    # User provided G-EYTF40N49B (Measurement ID) and AW-774994933 (Ads Account)
    TARGET_MEASUREMENT_ID = "G-EYTF40N49B" 
    ADS_CUSTOMER_ID = "774994933"
    
    print("--- Initializing Services ---")
    ga4_service = GA4Service()
    ads_connector = AdsConnector()
    
    # 1. Resolve GA4 Property ID
    print(f"\n--- Resolving Property ID for Measurement ID: {TARGET_MEASUREMENT_ID} ---")
    property_id = None
    
    # List all properties
    properties = ga4_service.list_properties()
    print(f"Found {len(properties)} accessible properties.")
    
    for prop in properties:
        p_id = prop['property_id']
        print(f"Checking Property: {prop['display_name']} ({p_id})")
        streams = ga4_service.list_data_streams(p_id)
        for stream in streams:
            m_id = stream.get('measurement_id')
            print(f"  - Stream: {stream['display_name']} ({m_id})")
            if m_id == TARGET_MEASUREMENT_ID:
                property_id = p_id
                print(f"FOUND MATCH: Property '{prop['display_name']}' ({p_id}) has Measurement ID {TARGET_MEASUREMENT_ID}")
                break
        if property_id:
            break
            
    if not property_id:
        print(f"Error: Could not find a GA4 Property with Measurement ID {TARGET_MEASUREMENT_ID}")
        # Fallback: If the user actually provided a Property ID (unlikely given format, but possible if they are confused)
        if TARGET_MEASUREMENT_ID.isdigit():
             print("Input looks like a Property ID, trying to use it directly...")
             property_id = TARGET_MEASUREMENT_ID
        else:
             return

    # 2. Link GA4 to Ads
    print(f"\n--- Linking GA4 Property {property_id} to Ads Account {ADS_CUSTOMER_ID} ---")
    link_result = ga4_service.create_google_ads_link(property_id, ADS_CUSTOMER_ID)
    print("Link Result:", link_result)
    
    # 3. Manage Conversion
    print(f"\n--- Checking/Activating 'purchase' Conversion in Ads Account {ADS_CUSTOMER_ID} ---")
    
    # List existing conversions
    conversions = ads_connector.get_conversion_actions(ADS_CUSTOMER_ID)
    target_conversion = None
    
    for conv in conversions:
        # Check for GA4 purchase
        # Name usually includes "purchase" and type is GA4
        if "purchase" in conv['name'].lower() and ("GA4" in conv['type'] or "GOOGLE_ANALYTICS" in conv['type']):
            target_conversion = conv
            print(f"Found existing GA4 purchase conversion: {conv['name']} ({conv['id']}) - Status: {conv['status']}")
            break
            
    if target_conversion:
        # Update it
        print(f"Updating conversion action {target_conversion['id']}...")
        update_result = ads_connector.update_conversion_action(
            ADS_CUSTOMER_ID, 
            target_conversion['id'],
            status='ENABLED',
            primary_for_goal=True,
            include_in_conversions_metric=True
        )
        print("Update Result:", update_result)
    else:
        print("GA4 Purchase conversion not found in Ads. It might need to be imported.")
        print("Note: Automatic import via API is complex. If the link was just created, it might take a moment to appear as importable.")
        print("Please check the Ads UI > Goals > Conversions > New conversion action > Import > GA4 Web.")

if __name__ == "__main__":
    main()
