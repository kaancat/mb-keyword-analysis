import sys
import os
print("Starting script...")
try:
    from dotenv import load_dotenv
    print("Imported dotenv")
    load_dotenv()
    print("Loaded .env")
    
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    print(f"Python path: {sys.path}")
    
    from backend.services.ads_connector import AdsConnector
    print("Imported AdsConnector")
    
    connector = AdsConnector()
    print("Initialized AdsConnector")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
