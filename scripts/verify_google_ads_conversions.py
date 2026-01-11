import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.ads_connector import AdsConnector
from dotenv import load_dotenv

def verify_conversions():
    load_dotenv()
    
    print("Initializing AdsConnector...")
    try:
        connector = AdsConnector()
    except Exception as e:
        print(f"Failed to initialize AdsConnector: {e}")
        return

    print("\n--- Listing Accessible Customers ---")
    customers = connector.get_accessible_customers()
    print(f"Found {len(customers)} accessible customers.")
    
    target_conversion_name = "booking_success"
    found_conversion = False

    for customer in customers:
        cid = str(customer['id'])
        name = customer['name']
        
        if "karim" not in name.lower():
            continue

        print(f"\nChecking Customer: {name} ({cid})")
        
        try:
            conversions = connector.get_conversion_actions(cid)
            print(f"  Found {len(conversions)} conversion actions.")
            
            for conv in conversions:
                print(f"  - {conv['name']} (ID: {conv['id']}, Type: {conv['type']}, Status: {conv['status']})")
                if target_conversion_name.lower() in conv['name'].lower():
                    print(f"  >>> MATCH FOUND: {conv['name']} <<<")
                    found_conversion = True
        except Exception as e:
            print(f"  Error fetching conversions for {name}: {e}")

    print("\n--- Verification Result ---")
    if found_conversion:
        print("SUCCESS: 'booking_success' conversion action found in one of the accounts.")
    else:
        print("WARNING: 'booking_success' conversion action NOT found in any accessible account.")

if __name__ == "__main__":
    verify_conversions()
