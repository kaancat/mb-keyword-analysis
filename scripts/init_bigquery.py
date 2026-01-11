import os
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv(Path.home() / ".mondaybrew" / ".env")

def init_bigquery():
    print("--- Initializing BigQuery ---")
    
    # Load credentials
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("BIGQUERY_PROJECT_ID")
    
    if not key_path or not os.path.exists(key_path):
        print(f"Error: Service account key not found at {key_path}")
        return

    print(f"Using Project ID: {project_id}")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(key_path)
        client = bigquery.Client(credentials=credentials, project=project_id)
        
        # Define dataset name
        dataset_id = f"{project_id}.ads_data"
        
        # Create dataset if it doesn't exist
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        
        try:
            client.get_dataset(dataset_id)
            print(f"Dataset {dataset_id} already exists.")
        except Exception:
            print(f"Dataset {dataset_id} not found. Creating...")
            dataset = client.create_dataset(dataset, timeout=30)
            print(f"Created dataset {client.project}.{dataset.dataset_id}")
            
        print("\n--- BigQuery Connection Successful! ---")
        
    except Exception as e:
        print(f"\nError connecting to BigQuery: {e}")

if __name__ == "__main__":
    init_bigquery()
