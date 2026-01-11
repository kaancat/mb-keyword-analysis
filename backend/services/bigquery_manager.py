import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env (or local .env fallback)
ensure_credentials()


class BigQueryManager:
    def __init__(self):
        self.project_id = os.getenv("BIGQUERY_PROJECT_ID")
        key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = bigquery.Client(credentials=credentials, project=self.project_id)
        self.dataset_id = f"{self.project_id}.ads_data"

    def ensure_campaign_table_exists(self):
        """Creates the campaign_performance table if it doesn't exist."""
        table_id = f"{self.dataset_id}.campaign_performance"

        schema = [
            bigquery.SchemaField("customer_id", "STRING"),
            bigquery.SchemaField("campaign_id", "STRING"),
            bigquery.SchemaField("campaign_name", "STRING"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("cost", "FLOAT"),
            bigquery.SchemaField("impressions", "INTEGER"),
            bigquery.SchemaField("clicks", "INTEGER"),
            bigquery.SchemaField("conversions", "FLOAT"),
            bigquery.SchemaField("ctr", "FLOAT"),
            bigquery.SchemaField("avg_cpc", "FLOAT"),
            bigquery.SchemaField("cpa", "FLOAT"),
        ]

        table = bigquery.Table(table_id, schema=schema)
        # Partition by date for efficiency
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, field="date"
        )

        try:
            self.client.get_table(table_id)
            print(f"Table {table_id} already exists.")
        except Exception:
            self.client.create_table(table)
            print(f"Created table {table_id}")

    def insert_campaign_data(self, rows):
        """Inserts a list of dictionaries into the campaign_performance table."""
        if not rows:
            return

        table_id = f"{self.dataset_id}.campaign_performance"

        # Deduplication strategy: Delete existing data for the dates we are inserting
        # For simplicity in MVP, we'll just append.
        # In production, we should use MERGE or delete-then-insert.

        errors = self.client.insert_rows_json(table_id, rows)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
        else:
            print(f"Successfully inserted {len(rows)} rows.")
