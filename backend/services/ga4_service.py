"""
Google Analytics 4 Service.
Access GA4 data via the Analytics Data API.
"""

import sys
from pathlib import Path

# Add plugin root to path for imports (works from any directory)
_plugin_root = Path(__file__).parent.parent.parent
if str(_plugin_root) not in sys.path:
    sys.path.insert(0, str(_plugin_root))

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter,
    OrderBy,
    CheckCompatibilityRequest,
    RunRealtimeReportRequest,
)
from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2.credentials import Credentials
import os
from typing import List, Optional, Dict, Any
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env - MUST succeed or raise error
_cred_source = ensure_credentials()
print(f"[GA4Service] Credentials loaded from: {_cred_source}")


class GA4Service:
    def __init__(self):
        # OAuth 2.0 Authentication (User Context)
        # Uses the same "Master Token" pattern as Sheets and Search Console

        client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")

        if not all([client_id, client_secret, refresh_token]):
            print("--- Error: Missing OAuth Credentials for GA4Service ---")
            print(
                "Ensure GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, and GOOGLE_ADS_REFRESH_TOKEN are set in .env"
            )
            self.client = None
            self.admin_client = None
            return

        try:
            self.creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=[
                    "https://www.googleapis.com/auth/analytics.readonly",
                    "https://www.googleapis.com/auth/analytics.edit",
                ],
            )

            self.client = BetaAnalyticsDataClient(credentials=self.creds)
            self.admin_client = AnalyticsAdminServiceClient(credentials=self.creds)
        except Exception as e:
            print(f"Failed to initialize GA4Service with OAuth: {e}")
            self.client = None
            self.admin_client = None

    # --- 1. Account & Property Discovery (Admin API) ---

    def list_accounts(self) -> List[Dict[str, Any]]:
        """Lists all GA4 accounts the service account has access to."""
        print("--- Listing GA4 Accounts ---")
        try:
            response = self.admin_client.list_accounts()
            accounts = []
            for account in response:
                accounts.append(
                    {
                        "account_id": account.name.split("/")[-1],
                        "name": account.name,
                        "display_name": account.display_name,
                        "region_code": account.region_code,
                        "create_time": str(account.create_time),
                        "update_time": str(account.update_time),
                    }
                )
            return accounts
        except Exception as e:
            print(f"Error listing accounts: {e}")
            return []

    def list_properties(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists properties. If account_id is provided, filters by that account.
        Otherwise lists all accessible properties.
        """
        # print(f"--- Listing GA4 Properties (Account: {account_id if account_id else 'All'}) ---")
        try:
            properties = []
            if account_id:
                response = self.admin_client.list_properties(
                    filter=f"parent:accounts/{account_id}", show_deleted=False
                )
                for prop in response:
                    properties.append(
                        {
                            "property_id": prop.name.split("/")[-1],
                            "name": prop.name,
                            "display_name": prop.display_name,
                            "account_name": prop.parent,
                        }
                    )
            else:
                # Use list_account_summaries for global view
                response = self.admin_client.list_account_summaries()
                for account in response:
                    for prop in account.property_summaries:
                        properties.append(
                            {
                                "property_id": prop.property.split("/")[-1],
                                "name": prop.property,
                                "display_name": prop.display_name,
                                "account_name": account.account,
                            }
                        )
            return properties
        except Exception as e:
            print(f"Error listing properties: {e}")
            return []

    def list_data_streams(self, property_id: str) -> List[Dict[str, Any]]:
        """Lists data streams for a given property."""
        try:
            response = self.admin_client.list_data_streams(
                parent=f"properties/{property_id}"
            )
            streams = []
            for stream in response:
                stream_data = {
                    "stream_id": stream.name.split("/")[-1],
                    "name": stream.name,
                    "type": stream.type_.name,
                    "display_name": stream.display_name,
                }
                if stream.web_stream_data:
                    stream_data["default_uri"] = stream.web_stream_data.default_uri
                    stream_data["measurement_id"] = (
                        stream.web_stream_data.measurement_id
                    )
                streams.append(stream_data)
            return streams
        except Exception as e:
            print(f"Error listing data streams for {property_id}: {e}")
            return []

    def list_bigquery_links(self, property_id: str) -> List[Dict[str, Any]]:
        """Lists BigQuery links for a property."""
        try:
            response = self.admin_client.list_big_query_links(
                parent=f"properties/{property_id}"
            )
            links = []
            for link in response:
                links.append(
                    {
                        "name": link.name,
                        "project_id": link.project,
                        "dataset_id": getattr(
                            link, "dataset_location", None
                        ),  # Attempt to get location/id
                    }
                )
            return links
        except Exception as e:
            return []

    def list_key_events(self, property_id: str) -> List[Dict[str, Any]]:
        """Lists key events (conversions) for a property."""
        try:
            # Try newer method name first, fallback to older
            if hasattr(self.admin_client, "list_key_events"):
                response = self.admin_client.list_key_events(
                    parent=f"properties/{property_id}"
                )
            else:
                response = self.admin_client.list_conversion_events(
                    parent=f"properties/{property_id}"
                )

            events = []
            for event in response:
                events.append(
                    {
                        "name": event.name,
                        "event_name": event.event_name,
                        "create_time": str(event.create_time),
                        "custom": event.custom,
                    }
                )
            return events
        except Exception as e:
            print(f"Error listing key events: {e}")
            return []

    def find_properties_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Finds properties that match a given domain via their data streams."""
        print(f"--- Finding Properties for Domain: {domain} ---")
        matches = []
        all_props = self.list_properties()

        target_domain = (
            domain.lower()
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
            .strip("/")
        )

        for prop in all_props:
            streams = self.list_data_streams(prop["property_id"])
            for stream in streams:
                if stream.get("default_uri"):
                    stream_uri = (
                        stream["default_uri"]
                        .lower()
                        .replace("https://", "")
                        .replace("http://", "")
                        .replace("www.", "")
                        .strip("/")
                    )
                    if target_domain in stream_uri or stream_uri in target_domain:
                        matches.append(
                            {
                                "property_id": prop["property_id"],
                                "display_name": prop["display_name"],
                                "account_name": prop["account_name"],
                                "domain": stream["default_uri"],
                                "stream_id": stream["stream_id"],
                            }
                        )
                        break
        return matches

    # --- 2. Generic Reporting Wrapper (Data API) ---

    def run_report(
        self,
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        start_date: str = "30daysAgo",
        end_date: str = "today",
        dimension_filter: Optional[FilterExpression] = None,
        metric_filter: Optional[FilterExpression] = None,
        limit: int = 10000,
        offset: int = 0,
        order_bys: Optional[List[Any]] = None,
        metric_aggregations: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generic wrapper for GA4 Data API runReport.
        """
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimension_filter=dimension_filter,
                metric_filter=metric_filter,
                limit=limit,
                offset=offset,
                order_bys=order_bys,
                metric_aggregations=metric_aggregations,
            )

            response = self.client.run_report(request)

            results = []
            for row in response.rows:
                item = {"dimensions": {}, "metrics": {}}
                for i, dim_val in enumerate(row.dimension_values):
                    item["dimensions"][dimensions[i]] = dim_val.value
                for i, met_val in enumerate(row.metric_values):
                    val = met_val.value
                    # Simple type conversion
                    if val.isdigit():
                        val = int(val)
                    elif val.replace(".", "", 1).isdigit():
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    item["metrics"][metrics[i]] = val
                results.append(item)
            return results
        except Exception as e:
            print(f"Error running report: {e}")
            return [{"error": str(e)}]

    def check_compatibility(
        self, property_id: str, dimensions: List[str], metrics: List[str]
    ) -> Dict[str, Any]:
        """Checks compatibility of dimensions and metrics."""
        try:
            request = CheckCompatibilityRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
            )
            response = self.client.check_compatibility(request)
            return {
                "dimension_compatibility": [
                    {
                        "name": c.dimension_metadata.api_name,
                        "compatibility": c.compatibility.name,
                    }
                    for c in response.dimension_compatibilities
                ],
                "metric_compatibility": [
                    {
                        "name": c.metric_metadata.api_name,
                        "compatibility": c.compatibility.name,
                    }
                    for c in response.metric_compatibilities
                ],
            }
        except Exception as e:
            return {"error": str(e)}

    def run_realtime_report(
        self,
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        limit: int = 10000,
        dimension_filter: Optional[FilterExpression] = None,
        metric_filter: Optional[FilterExpression] = None,
    ) -> List[Dict[str, Any]]:
        """Runs a realtime report."""
        try:
            request = RunRealtimeReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                dimension_filter=dimension_filter,
                metric_filter=metric_filter,
                limit=limit,
            )
            response = self.client.run_realtime_report(request)

            results = []
            for row in response.rows:
                item = {"dimensions": {}, "metrics": {}}
                for i, dim_val in enumerate(row.dimension_values):
                    item["dimensions"][dimensions[i]] = dim_val.value
                for i, met_val in enumerate(row.metric_values):
                    val = met_val.value
                    if val.isdigit():
                        val = int(val)
                    elif val.replace(".", "", 1).isdigit():
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    item["metrics"][metrics[i]] = val
                results.append(item)
            return results
        except Exception as e:
            print(f"Error running realtime report: {e}")
            return [{"error": str(e)}]

    # --- 3. Opinionated Convenience Methods ---

    def get_behavior_metrics(
        self, property_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Fetches core behavior metrics using run_report."""
        # print(f"--- Fetching Behavior Metrics for {property_id} ---")
        dims = ["sessionDefaultChannelGroup"]
        mets = [
            "sessions",
            "engagementRate",
            "averageSessionDuration",
            "screenPageViewsPerSession",
            "conversions",
        ]

        data = self.run_report(
            property_id, dims, mets, start_date=f"{days}daysAgo", end_date="today"
        )

        if data and "error" in data[0]:
            return data

        results = []
        for row in data:
            metrics = row["metrics"]
            dims_res = row["dimensions"]
            results.append(
                {
                    "channel": dims_res["sessionDefaultChannelGroup"],
                    "sessions": metrics["sessions"],
                    "engagement_rate": (
                        f"{metrics['engagementRate'] * 100:.1f}%"
                        if isinstance(metrics["engagementRate"], (int, float))
                        else metrics["engagementRate"]
                    ),
                    "avg_duration_sec": (
                        round(metrics["averageSessionDuration"], 1)
                        if isinstance(metrics["averageSessionDuration"], (int, float))
                        else metrics["averageSessionDuration"]
                    ),
                    "pages_per_session": (
                        round(metrics["screenPageViewsPerSession"], 1)
                        if isinstance(
                            metrics["screenPageViewsPerSession"], (int, float)
                        )
                        else metrics["screenPageViewsPerSession"]
                    ),
                    "conversions": metrics["conversions"],
                }
            )
        return results

    def get_conversion_breakdown(
        self, property_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Fetches conversions broken down by event name."""
        dims = ["eventName"]
        mets = ["conversions"]

        data = self.run_report(
            property_id, dims, mets, start_date=f"{days}daysAgo", end_date="today"
        )

        if data and "error" in data[0]:
            return []

        results = []
        for row in data:
            convs = row["metrics"]["conversions"]
            # Ensure convs is a number before comparison
            if isinstance(convs, (int, float)) and convs > 0:
                results.append(
                    {"event_name": row["dimensions"]["eventName"], "conversions": convs}
                )

        results.sort(key=lambda x: x["conversions"], reverse=True)
        return results

    def get_top_pages(
        self, property_id: str, days: int = 30, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetches top pages by views."""
        dims = ["pagePath"]
        mets = ["screenPageViews", "sessions", "conversions"]

        order_bys = [
            OrderBy(
                metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True
            )
        ]

        data = self.run_report(
            property_id,
            dims,
            mets,
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
            order_bys=order_bys,
        )

        if data and "error" in data[0]:
            return []

        results = []
        for row in data:
            results.append(
                {
                    "page_path": row["dimensions"]["pagePath"],
                    "views": row["metrics"]["screenPageViews"],
                    "sessions": row["metrics"]["sessions"],
                    "conversions": row["metrics"]["conversions"],
                }
            )
        return results

    def get_traffic_sources(
        self, property_id: str, days: int = 30, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetches traffic sources."""
        dims = ["sessionSourceMedium"]
        mets = ["sessions", "conversions"]

        order_bys = [
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)
        ]

        data = self.run_report(
            property_id,
            dims,
            mets,
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
            order_bys=order_bys,
        )

        if data and "error" in data[0]:
            return []

        results = []
        for row in data:
            results.append(
                {
                    "source_medium": row["dimensions"]["sessionSourceMedium"],
                    "sessions": row["metrics"]["sessions"],
                    "conversions": row["metrics"]["conversions"],
                }
            )
        return results

    def create_google_ads_link(
        self,
        property_id: str,
        customer_id: str,
        ads_personalization_enabled: bool = True,
    ) -> Dict[str, Any]:
        """Creates a link between a GA4 property and a Google Ads account."""
        print(
            f"--- Creating Google Ads Link for Property {property_id} to Account {customer_id} ---"
        )
        try:
            # Construct the link
            # Note: customer_id should be the 10-digit ID (e.g., '1234567890')
            link = {
                "customer_id": customer_id.replace("-", ""),
                "ads_personalization_enabled": ads_personalization_enabled,
            }

            parent = f"properties/{property_id}"

            # The client library method signature might vary slightly depending on version,
            # but generally takes parent and google_ads_link
            from google.analytics.admin_v1alpha.types import GoogleAdsLink

            google_ads_link = GoogleAdsLink(
                customer_id=customer_id.replace("-", ""),
                ads_personalization_enabled=ads_personalization_enabled,
            )

            response = self.admin_client.create_google_ads_link(
                parent=parent, google_ads_link=google_ads_link
            )

            return {
                "name": response.name,
                "create_time": str(response.create_time),
                "customer_id": response.customer_id,
            }
        except Exception as e:
            print(f"Error creating Google Ads link: {e}")
            return {"error": str(e)}

    def list_accessible_properties(self):
        """Deprecated: Use list_properties() instead."""
        return self.list_properties()


if __name__ == "__main__":
    # Test
    service = GA4Service()
    print("--- Testing Discovery ---")
    props = service.list_properties()
    print(f"Found {len(props)} properties")
    if props:
        p_id = props[0]["property_id"]
        print(f"Testing with property: {props[0]['display_name']} ({p_id})")

        print("\n--- Data Streams ---")
        print(service.list_data_streams(p_id))

        print("\n--- Behavior Metrics ---")
        print(service.get_behavior_metrics(p_id, days=7))

        print("\n--- Top Pages ---")
        print(service.get_top_pages(p_id, days=7, limit=5))
