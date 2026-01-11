"""
Google Ads Connector.
Full read/write access to Google Ads accounts via the Google Ads API.
"""

import sys
from pathlib import Path

# Add plugin root to path for imports (works from any directory)
_plugin_root = Path(__file__).parent.parent.parent
if str(_plugin_root) not in sys.path:
    sys.path.insert(0, str(_plugin_root))

import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers
import pandas as pd
from datetime import datetime, timedelta
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env - MUST succeed or raise error
_cred_source = ensure_credentials()
print(f"[AdsConnector] Credentials loaded from: {_cred_source}")


class AdsConnector:
    def __init__(self):
        try:
            config = {
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
                "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
                "login_customer_id": os.getenv(
                    "GOOGLE_ADS_LOGIN_CUSTOMER_ID", ""
                ).strip(),
                "use_proto_plus": "True",
            }
            print(
                f"DEBUG: Config login_customer_id: '{config['login_customer_id']}' (Type: {type(config['login_customer_id'])})"
            )
            self.client = GoogleAdsClient.load_from_dict(config)
            self.ga_service = self.client.get_service("GoogleAdsService")
        except Exception as e:
            print(f"Failed to initialize AdsConnector: {e}")
            raise e

    def get_accessible_customers(self):
        """Returns a list of customer IDs accessible by the login customer."""
        customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        query = """
            SELECT
                customer_client.client_customer,
                customer_client.level,
                customer_client.descriptive_name,
                customer_client.id
            FROM customer_client
            WHERE customer_client.level <= 1
        """

        accounts = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    client = row.customer_client
                    # Only add leaf accounts (not the MCC itself if it shows up)
                    if client.id != int(customer_id):
                        accounts.append(
                            {"name": client.descriptive_name, "id": str(client.id)}
                        )
        except GoogleAdsException as ex:
            print(f"Error fetching accounts: {ex}")

        return accounts

    def get_auction_insights(self, customer_id, date_range="LAST_30_DAYS"):
        """
        Fetches auction insights for campaigns.
        """
        query = f"""
            SELECT
                segments.date,
                campaign.id,
                campaign.name,
                segments.auction_insight_domain,
                metrics.auction_insight_search_impression_share,
                metrics.auction_insight_search_outranking_share,
                metrics.auction_insight_search_overlap_rate,
                metrics.auction_insight_search_position_above_rate
            FROM campaign_auction_insight
            WHERE segments.date DURING {date_range}
                AND campaign.status != 'REMOVED'
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            data = []
            for batch in response:
                for row in batch.results:
                    data.append(
                        {
                            "date": row.segments.date,
                            "campaign_id": row.campaign.id,
                            "campaign_name": row.campaign.name,
                            "competitor_domain": row.segments.auction_insight_domain,
                            "impression_share": row.metrics.auction_insight_search_impression_share,
                            "outranking_share": row.metrics.auction_insight_search_outranking_share,
                            "overlap_rate": row.metrics.auction_insight_search_overlap_rate,
                            "position_above_rate": row.metrics.auction_insight_search_position_above_rate,
                        }
                    )
            return pd.DataFrame(data)
        except GoogleAdsException as ex:
            print(
                f"Request with ID '{ex.request_id}' failed with status '{ex.error.code().name}' and includes the following errors:"
            )
            for error in ex.failure.errors:
                print(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"\t\tOn field: {field_path_element.field_name}")
            return pd.DataFrame()

    def get_campaign_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetches campaign performance for a specific customer."""

        # If date_range is a string like 'LAST_30_DAYS', we use it in the WHERE clause.
        # But for BigQuery sync, we usually want specific dates.
        # For MVP, let's just fetch YESTERDAY by default if no range specified.

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                segments.date,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share
            FROM campaign
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "customer_id": str(customer_id),
                            "campaign_id": str(row.campaign.id),
                            "campaign_name": row.campaign.name,
                            "status": row.campaign.status.name,
                            "date": row.segments.date,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "impressions": row.metrics.impressions,
                            "clicks": row.metrics.clicks,
                            "conversions": row.metrics.conversions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cpa": (
                                row.metrics.cost_per_conversion / 1000000.0
                                if row.metrics.cost_per_conversion
                                else 0
                            ),
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching campaign data for {customer_id}: {ex}")

        return rows

    def get_ad_group_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetches ad group level performance data."""
        query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                campaign.id,
                campaign.name,
                segments.date,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.cost_per_conversion,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share
            FROM ad_group
            WHERE segments.date DURING {date_range}
                AND ad_group.status != 'REMOVED'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "ad_group_id": str(row.ad_group.id),
                            "ad_group_name": row.ad_group.name,
                            "status": row.ad_group.status.name,
                            "type": row.ad_group.type_.name,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                            "cpa": (
                                row.metrics.cost_per_conversion / 1000000.0
                                if row.metrics.cost_per_conversion
                                else 0
                            ),
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching ad group data for {customer_id}: {ex}")
        return rows

    def get_keyword_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetches keyword performance with Quality Scores."""
        query = f"""
            SELECT
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.creative_quality_score,
                ad_group_criterion.quality_info.post_click_quality_score,
                ad_group_criterion.quality_info.search_predicted_ctr,
                campaign.name,
                ad_group.name,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.cost_per_conversion
            FROM keyword_view
            WHERE segments.date DURING {date_range}
                AND ad_group_criterion.status != 'REMOVED'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    kw = row.ad_group_criterion
                    qs = kw.quality_info
                    rows.append(
                        {
                            "keyword": kw.keyword.text,
                            "match_type": kw.keyword.match_type.name,
                            "status": kw.status.name,
                            "quality_score": (
                                qs.quality_score if qs.quality_score else 0
                            ),
                            "creative_qs": (
                                qs.creative_quality_score.name
                                if qs.creative_quality_score
                                else "UNKNOWN"
                            ),
                            "landing_page_qs": (
                                qs.post_click_quality_score.name
                                if qs.post_click_quality_score
                                else "UNKNOWN"
                            ),
                            "expected_ctr": (
                                qs.search_predicted_ctr.name
                                if qs.search_predicted_ctr
                                else "UNKNOWN"
                            ),
                            "campaign_name": row.campaign.name,
                            "ad_group_name": row.ad_group.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                            "cpa": (
                                row.metrics.cost_per_conversion / 1000000.0
                                if row.metrics.cost_per_conversion
                                else 0
                            ),
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching keyword data for {customer_id}: {ex}")
        return rows

    def get_search_terms(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetch search terms report - critical for negative keyword discovery."""
        query = f"""
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                segments.keyword.info.match_type,
                campaign.name,
                ad_group.name,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.cost_per_conversion
            FROM search_term_view
            WHERE segments.date DURING {date_range}
            ORDER BY metrics.cost_micros DESC
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "search_term": row.search_term_view.search_term,
                            "status": row.search_term_view.status.name,
                            "match_type": (
                                row.segments.keyword.info.match_type.name
                                if row.segments.keyword.info.match_type
                                else "UNKNOWN"
                            ),
                            "campaign_name": row.campaign.name,
                            "ad_group_name": row.ad_group.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                            "cpa": (
                                row.metrics.cost_per_conversion / 1000000.0
                                if row.metrics.cost_per_conversion
                                else 0
                            ),
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching search terms for {customer_id}: {ex}")
        return rows

    def get_ad_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetch RSA ad performance including ad strength."""
        query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.type,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.final_urls,
                ad_group_ad.status,
                ad_group_ad.ad_strength,
                ad_group_ad.policy_summary.approval_status,
                campaign.name,
                ad_group.name,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad
            WHERE segments.date DURING {date_range}
                AND ad_group_ad.status != 'REMOVED'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    ad = row.ad_group_ad

                    # Extract RSA headlines and descriptions
                    headlines = []
                    descriptions = []
                    if (
                        ad.ad.type_.name == "RESPONSIVE_SEARCH_AD"
                    ):  # Check type name string or enum
                        # Note: GoogleAdsClient enums are usually accessed via client.enums...
                        # but here we can just check the string if we want to be safe or use the property if accessible.
                        # The user provided code uses `self.client.enums.AdTypeEnum.RESPONSIVE_SEARCH_AD` but `ad.ad.type_` returns an enum wrapper.
                        # Using `.name` comparison is often safer/easier without importing the enum class.

                        if hasattr(ad.ad, "responsive_search_ad"):
                            for headline in ad.ad.responsive_search_ad.headlines:
                                headlines.append(
                                    {
                                        "text": headline.text,
                                        "pinned_field": (
                                            headline.pinned_field.name
                                            if headline.pinned_field
                                            else None
                                        ),
                                    }
                                )
                            for desc in ad.ad.responsive_search_ad.descriptions:
                                descriptions.append(
                                    {
                                        "text": desc.text,
                                        "pinned_field": (
                                            desc.pinned_field.name
                                            if desc.pinned_field
                                            else None
                                        ),
                                    }
                                )

                    rows.append(
                        {
                            "ad_id": str(ad.ad.id),
                            "type": ad.ad.type_.name,
                            "headlines": headlines,
                            "descriptions": descriptions,
                            "final_urls": list(ad.ad.final_urls),
                            "status": ad.status.name,
                            "ad_strength": ad.ad_strength.name,
                            "approval_status": ad.policy_summary.approval_status.name,
                            "campaign_name": row.campaign.name,
                            "ad_group_name": row.ad_group.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching ad performance for {customer_id}: {ex}")
        return rows

    def get_conversion_actions(self, customer_id):
        """List all conversion actions."""
        query = """
            SELECT
                conversion_action.id,
                conversion_action.name,
                conversion_action.type,
                conversion_action.status,
                conversion_action.category,
                conversion_action.counting_type
            FROM conversion_action
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    ca = row.conversion_action
                    rows.append(
                        {
                            "id": str(ca.id),
                            "name": ca.name,
                            "type": ca.type_.name,
                            "status": ca.status.name,
                            "category": ca.category.name,
                            "conversions": 0,  # Metrics not available in this view
                            "value": 0,
                            "all_conversions": 0,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching conversion actions for {customer_id}: {ex}")
        return rows

    def update_conversion_action(self, customer_id, conversion_action_id, **kwargs):
        """
        Updates a conversion action.
        kwargs: fields to update (e.g., status='ENABLED', primary_for_goal=True, include_in_conversions_metric=True)
        """
        print(
            f"--- Updating Conversion Action {conversion_action_id} for Customer {customer_id} ---"
        )
        try:
            conversion_action_service = self.client.get_service(
                "ConversionActionService"
            )
            operation = self.client.get_type("ConversionActionOperation")

            # Create the update mask
            update = operation.update
            update.resource_name = self.ga_service.conversion_action_path(
                customer_id, conversion_action_id
            )

            # Apply updates based on kwargs
            for key, value in kwargs.items():
                if hasattr(update, key):
                    setattr(update, key, value)
                    self.client.copy_from(
                        operation.update_mask,
                        protobuf_helpers.field_mask(None, update._pb),
                    )
                else:
                    print(f"Warning: Field '{key}' not found on ConversionAction")

            # Issue the mutation
            response = conversion_action_service.mutate_conversion_actions(
                customer_id=customer_id, operations=[operation]
            )

            return {"resource_name": response.results[0].resource_name}
        except GoogleAdsException as ex:
            print(f"Error updating conversion action: {ex}")
            return {"error": str(ex)}

    def create_conversion_action(
        self,
        customer_id,
        name,
        type_="UPLOAD_CLICKS",
        category="LEAD",
        value_settings=None,
        counting_type="ONE_PER_CLICK",
    ):
        """
        Create a new conversion action.

        Args:
            customer_id: Google Ads customer ID
            name: Name of the conversion action
            type_: Type of conversion (UPLOAD_CLICKS for offline, WEBPAGE for website, etc.)
            category: Category (LEAD, PURCHASE, etc.)
            value_settings: Optional dict with 'default_value' and 'default_currency_code'
            counting_type: ONE_PER_CLICK or MANY_PER_CLICK

        Returns:
            Dict with 'id', 'resource_name' or 'error'
        """
        print(f"--- Creating Conversion Action '{name}' for Customer {customer_id} ---")
        try:
            conversion_action_service = self.client.get_service(
                "ConversionActionService"
            )
            operation = self.client.get_type("ConversionActionOperation")

            conversion_action = operation.create
            conversion_action.name = name
            conversion_action.type_ = getattr(
                self.client.enums.ConversionActionTypeEnum, type_
            )
            conversion_action.category = getattr(
                self.client.enums.ConversionActionCategoryEnum, category
            )
            conversion_action.status = (
                self.client.enums.ConversionActionStatusEnum.ENABLED
            )
            conversion_action.counting_type = getattr(
                self.client.enums.ConversionActionCountingTypeEnum, counting_type
            )

            # Set value settings if provided
            if value_settings:
                conversion_action.value_settings.default_value = value_settings.get(
                    "default_value", 0
                )
                conversion_action.value_settings.default_currency_code = (
                    value_settings.get("default_currency_code", "DKK")
                )
                conversion_action.value_settings.always_use_default_value = (
                    value_settings.get("always_use_default", False)
                )

            # Issue the mutation
            response = conversion_action_service.mutate_conversion_actions(
                customer_id=customer_id, operations=[operation]
            )

            resource_name = response.results[0].resource_name
            # Extract ID from resource name (format: customers/123/conversionActions/456)
            conversion_id = resource_name.split("/")[-1]

            print(f"Created conversion action: {name}")
            print(f"  Resource Name: {resource_name}")
            print(f"  ID: {conversion_id}")

            return {"id": conversion_id, "resource_name": resource_name}
        except GoogleAdsException as ex:
            print(f"Error creating conversion action: {ex}")
            return {"error": str(ex)}

    def get_geographic_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetch performance by geographic location."""
        query = f"""
            SELECT
                geographic_view.country_criterion_id,
                geographic_view.location_type,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM geographic_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "country_id": str(row.geographic_view.country_criterion_id),
                            "location_type": row.geographic_view.location_type.name,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching geographic data for {customer_id}: {ex}")
        return rows

    def get_device_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Fetch performance by device type."""
        query = f"""
            SELECT
                segments.device,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "device": row.segments.device.name,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "ctr": row.metrics.ctr,
                            "avg_cpc": (
                                row.metrics.average_cpc / 1000000.0
                                if row.metrics.average_cpc
                                else 0
                            ),
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching device data for {customer_id}: {ex}")
        return rows

    def get_change_history(self, customer_id, days=14):
        """Fetch recent changes to the account."""
        # Calculate date range for change history manually as it doesn't support DURING syntax the same way in all contexts,
        # but here we use DURING LAST_14_DAYS as requested.

        query = """
            SELECT
                change_event.change_date_time,
                change_event.change_resource_type,
                change_event.change_resource_name,
                change_event.client_type,
                change_event.user_email,
                change_event.old_resource,
                change_event.new_resource,
                change_event.resource_change_operation
            FROM change_event
            WHERE change_event.change_date_time DURING LAST_14_DAYS
            ORDER BY change_event.change_date_time DESC
            LIMIT 1000
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    ce = row.change_event
                    rows.append(
                        {
                            "date": ce.change_date_time,
                            "type": ce.change_resource_type.name,
                            "resource": ce.change_resource_name,
                            "user": ce.user_email,
                            "operation": ce.resource_change_operation.name,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching change history for {customer_id}: {ex}")
        return rows

    def get_recommendations(self, customer_id):
        """Fetch Google's recommendations for the account."""
        query = """
            SELECT
                recommendation.resource_name,
                recommendation.type,
                recommendation.impact,
                recommendation.campaign,
                recommendation.ad_group
            FROM recommendation
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rec = row.recommendation
                    rows.append(
                        {
                            "type": rec.type_.name,
                            "resource": rec.resource_name,
                            "campaign": rec.campaign,
                            "ad_group": rec.ad_group,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching recommendations for {customer_id}: {ex}")
        return rows

    def get_asset_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Get asset-level performance with Google's performance labels (BEST/GOOD/LOW/LEARNING)."""
        query = f"""
            SELECT
                ad_group_ad_asset_view.ad_group_ad,
                ad_group_ad_asset_view.asset,
                ad_group_ad_asset_view.field_type,
                ad_group_ad_asset_view.performance_label,
                asset.text_asset.text,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad_asset_view
            WHERE segments.date DURING {date_range}
            ORDER BY ad_group_ad_asset_view.performance_label
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    view = row.ad_group_ad_asset_view
                    rows.append(
                        {
                            "asset_id": str(view.asset),
                            "field_type": view.field_type.name,
                            "performance_label": view.performance_label.name,
                            "text": row.asset.text_asset.text,
                            "impressions": row.metrics.impressions,
                            "clicks": row.metrics.clicks,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching asset performance for {customer_id}: {ex}")
        return rows

    def get_landing_page_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Analyze landing page effectiveness."""
        query = f"""
            SELECT
                landing_page_view.unexpanded_final_url,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.mobile_friendly_clicks_percentage,
                metrics.valid_accelerated_mobile_pages_clicks_percentage,
                metrics.speed_score
            FROM landing_page_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "url": row.landing_page_view.unexpanded_final_url,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                            "mobile_friendly_click_pct": row.metrics.mobile_friendly_clicks_percentage,
                            "speed_score": row.metrics.speed_score,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching landing page performance for {customer_id}: {ex}")
        return rows

    def get_expanded_landing_page_performance(
        self, customer_id, date_range="LAST_30_DAYS"
    ):
        """Get performance for each unique final URL."""
        query = f"""
            SELECT
                expanded_landing_page_view.expanded_final_url,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM expanded_landing_page_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "url": row.expanded_landing_page_view.expanded_final_url,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(
                f"Error fetching expanded landing page performance for {customer_id}: {ex}"
            )
        return rows

    def get_user_location_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Get performance by actual user location (not just targeted locations)."""
        query = f"""
            SELECT
                user_location_view.country_criterion_id,
                user_location_view.targeting_location,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM user_location_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "country_id": str(
                                row.user_location_view.country_criterion_id
                            ),
                            "targeting_location": row.user_location_view.targeting_location,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching user location performance for {customer_id}: {ex}")
        return rows

    def get_impression_share_data(self, customer_id, date_range="LAST_30_DAYS"):
        """Get detailed impression share metrics."""
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                metrics.search_impression_share,
                metrics.search_top_impression_share,
                metrics.search_absolute_top_impression_share,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share,
                metrics.search_budget_lost_top_impression_share,
                metrics.search_rank_lost_top_impression_share,
                metrics.search_budget_lost_absolute_top_impression_share,
                metrics.search_rank_lost_absolute_top_impression_share
            FROM campaign
            WHERE segments.date DURING {date_range}
                AND campaign.advertising_channel_type = 'SEARCH'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "campaign_name": row.campaign.name,
                            "search_is": row.metrics.search_impression_share,
                            "search_top_is": row.metrics.search_top_impression_share,
                            "search_abs_top_is": row.metrics.search_absolute_top_impression_share,
                            "lost_is_budget": row.metrics.search_budget_lost_impression_share,
                            "lost_is_rank": row.metrics.search_rank_lost_impression_share,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching impression share data for {customer_id}: {ex}")
        return rows

    def get_campaign_budgets(self, customer_id):
        """Get campaign budget details."""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.campaign_budget,
                campaign_budget.amount_micros,
                campaign_budget.delivery_method,
                campaign_budget.period,
                campaign_budget.type,
                campaign_budget.explicitly_shared,
                metrics.cost_micros
            FROM campaign
            WHERE campaign.status != 'REMOVED'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "campaign_name": row.campaign.name,
                            "budget_resource": row.campaign.campaign_budget,
                            "amount": row.campaign_budget.amount_micros / 1000000.0,
                            "delivery_method": row.campaign_budget.delivery_method.name,
                            "period": row.campaign_budget.period.name,
                            "type": row.campaign_budget.type_.name,
                            "shared": row.campaign_budget.explicitly_shared,
                            "cost": row.metrics.cost_micros / 1000000.0,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching campaign budgets for {customer_id}: {ex}")
        return rows

    def get_bidding_strategies(self, customer_id):
        """Analyze bidding strategies in use."""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.bidding_strategy_type,
                campaign.maximize_conversions.target_cpa_micros,
                campaign.maximize_conversion_value.target_roas,
                campaign.target_cpa.target_cpa_micros,
                campaign.target_roas.target_roas,
                accessible_bidding_strategy.id,
                accessible_bidding_strategy.name,
                accessible_bidding_strategy.type,
                accessible_bidding_strategy.maximize_conversions.target_cpa_micros,
                accessible_bidding_strategy.target_cpa.target_cpa_micros
            FROM campaign
            WHERE campaign.status != 'REMOVED'
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    c = row.campaign
                    rows.append(
                        {
                            "campaign_name": c.name,
                            "type": c.bidding_strategy_type.name,
                            "target_cpa": (
                                c.maximize_conversions.target_cpa_micros / 1000000.0
                                if c.maximize_conversions.target_cpa_micros
                                else (
                                    c.target_cpa.target_cpa_micros / 1000000.0
                                    if c.target_cpa.target_cpa_micros
                                    else None
                                )
                            ),
                            "target_roas": (
                                c.maximize_conversion_value.target_roas
                                if c.maximize_conversion_value.target_roas
                                else (
                                    c.target_roas.target_roas
                                    if c.target_roas.target_roas
                                    else None
                                )
                            ),
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching bidding strategies for {customer_id}: {ex}")
        return rows

    def get_paid_organic_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Compare paid vs organic search performance."""
        query = f"""
            SELECT
                paid_organic_search_term_view.search_term,
                metrics.combined_clicks,
                metrics.combined_queries,
                metrics.organic_clicks,
                metrics.organic_queries,
                metrics.organic_impressions
            FROM paid_organic_search_term_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "search_term": row.paid_organic_search_term_view.search_term,
                            "combined_clicks": row.metrics.combined_clicks,
                            "organic_clicks": row.metrics.organic_clicks,
                            "organic_impressions": row.metrics.organic_impressions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching paid/organic data for {customer_id}: {ex}")
        return rows

    def get_click_data(self, customer_id, date_range="YESTERDAY"):
        """Get click-level data with GCLID - useful for conversion debugging. Note: ClickView requires single day query."""
        query = f"""
            SELECT
                click_view.gclid,
                click_view.area_of_interest.city,
                click_view.area_of_interest.country,
                click_view.keyword,
                click_view.keyword_info.text,
                click_view.keyword_info.match_type,
                click_view.ad_group_ad,
                campaign.name,
                ad_group.name
            FROM click_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "gclid": row.click_view.gclid,
                            "city": row.click_view.area_of_interest.city,
                            "country": row.click_view.area_of_interest.country,
                            "keyword": row.click_view.keyword_info.text,
                            "campaign_name": row.campaign.name,
                            "ad_group_name": row.ad_group.name,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching click data for {customer_id}: {ex}")
        return rows

    def get_ad_schedule_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Analyze performance by hour/day of week."""
        query = f"""
            SELECT
                segments.hour,
                segments.day_of_week,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "hour": row.segments.hour,
                            "day": row.segments.day_of_week.name,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching ad schedule for {customer_id}: {ex}")
        return rows

    def get_audience_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Get performance by audience segments."""
        query = f"""
            SELECT
                campaign_audience_view.resource_name,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign_audience_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "resource": row.campaign_audience_view.resource_name,
                            "campaign_name": row.campaign.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching audience performance for {customer_id}: {ex}")
        return rows

    def get_demographic_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """Get performance by age and gender demographics."""
        # Note: Age and Gender are separate views. We'll fetch age here as requested in the query example.
        # The user's query example selects from 'age_range_view' but also selects 'gender.type' which is invalid.
        # You can't select gender from age_range_view. We need two queries or just one.
        # I will implement Age Range view as per the FROM clause in the user's example.

        query = f"""
            SELECT
                ad_group_criterion.age_range.type,
                campaign.name,
                ad_group.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions
            FROM age_range_view
            WHERE segments.date DURING {date_range}
        """

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "age_range": row.ad_group_criterion.age_range.type_.name,
                            "campaign_name": row.campaign.name,
                            "ad_group_name": row.ad_group.name,
                            "clicks": row.metrics.clicks,
                            "impressions": row.metrics.impressions,
                            "cost": row.metrics.cost_micros / 1000000.0,
                            "conversions": row.metrics.conversions,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching demographic data for {customer_id}: {ex}")
        return rows

    # ============================================
    # WRITE OPERATIONS - Negative Keywords
    # ============================================

    def add_campaign_negative_keywords(self, customer_id, campaign_id, keywords):
        """
        Add negative keywords to a campaign (campaign-level negatives).

        Args:
            customer_id: The Google Ads customer ID
            campaign_id: The campaign ID to add negatives to
            keywords: List of keyword strings (without - prefix)

        Returns:
            dict with results and any errors
        """
        campaign_criterion_service = self.client.get_service("CampaignCriterionService")

        operations = []
        for keyword in keywords:
            # Create the operation
            operation = self.client.get_type("CampaignCriterionOperation")
            criterion = operation.create

            # Set the campaign
            criterion.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Set as negative
            criterion.negative = True

            # Set the keyword
            criterion.keyword.text = keyword
            criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum.PHRASE

            operations.append(operation)

        results = {"added": [], "errors": []}

        try:
            response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=customer_id, operations=operations
            )

            for result in response.results:
                results["added"].append(result.resource_name)

            print(
                f"Added {len(results['added'])} negative keywords to campaign {campaign_id}"
            )

        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                results["errors"].append(
                    {
                        "message": error.message,
                        "keyword": (
                            keywords[0] if keywords else "unknown"
                        ),  # Simplified error tracking
                    }
                )
            print(f"Error adding negative keywords: {ex}")

        return results

    def add_shared_negative_keyword_list(self, customer_id, list_name, keywords):
        """
        Create a shared negative keyword list and add keywords to it.

        Args:
            customer_id: The Google Ads customer ID
            list_name: Name for the shared list
            keywords: List of keyword strings

        Returns:
            dict with list resource name and results
        """
        shared_set_service = self.client.get_service("SharedSetService")
        shared_criterion_service = self.client.get_service("SharedCriterionService")

        results = {"list_resource": None, "added": [], "errors": []}

        try:
            # Step 1: Create the shared negative keyword list
            shared_set_operation = self.client.get_type("SharedSetOperation")
            shared_set = shared_set_operation.create
            shared_set.name = list_name
            shared_set.type_ = self.client.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS

            response = shared_set_service.mutate_shared_sets(
                customer_id=customer_id, operations=[shared_set_operation]
            )

            shared_set_resource = response.results[0].resource_name
            results["list_resource"] = shared_set_resource
            print(f"Created shared negative keyword list: {list_name}")

            # Step 2: Add keywords to the shared list
            operations = []
            for keyword in keywords:
                operation = self.client.get_type("SharedCriterionOperation")
                criterion = operation.create
                criterion.shared_set = shared_set_resource
                criterion.keyword.text = keyword
                criterion.keyword.match_type = (
                    self.client.enums.KeywordMatchTypeEnum.PHRASE
                )
                operations.append(operation)

            response = shared_criterion_service.mutate_shared_criteria(
                customer_id=customer_id, operations=operations
            )

            for result in response.results:
                results["added"].append(result.resource_name)

            print(f"Added {len(results['added'])} keywords to shared list")

        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                results["errors"].append(error.message)
            print(f"Error creating shared list: {ex}")

        return results

    def attach_shared_set_to_campaign(
        self, customer_id, campaign_id, shared_set_resource
    ):
        """
        Attach a shared negative keyword list to a campaign.

        Args:
            customer_id: The Google Ads customer ID
            campaign_id: The campaign ID
            shared_set_resource: Resource name of the shared set

        Returns:
            dict with result
        """
        campaign_shared_set_service = self.client.get_service(
            "CampaignSharedSetService"
        )

        try:
            operation = self.client.get_type("CampaignSharedSetOperation")
            campaign_shared_set = operation.create
            campaign_shared_set.campaign = (
                f"customers/{customer_id}/campaigns/{campaign_id}"
            )
            campaign_shared_set.shared_set = shared_set_resource

            response = campaign_shared_set_service.mutate_campaign_shared_sets(
                customer_id=customer_id, operations=[operation]
            )

            print(f"Attached shared set to campaign {campaign_id}")
            return {"success": True, "resource": response.results[0].resource_name}

        except GoogleAdsException as ex:
            print(f"Error attaching shared set: {ex}")
            return {"success": False, "error": str(ex)}

    def get_existing_negative_keywords(self, customer_id, campaign_id=None):
        """
        Get existing negative keywords for a campaign or account.

        Args:
            customer_id: The Google Ads customer ID
            campaign_id: Optional campaign ID to filter by

        Returns:
            List of existing negative keywords
        """
        query = """
            SELECT
                campaign_criterion.keyword.text,
                campaign_criterion.keyword.match_type,
                campaign_criterion.negative,
                campaign.id,
                campaign.name
            FROM campaign_criterion
            WHERE campaign_criterion.type = 'KEYWORD'
                AND campaign_criterion.negative = TRUE
        """

        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"

        rows = []
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            for batch in response:
                for row in batch.results:
                    rows.append(
                        {
                            "keyword": row.campaign_criterion.keyword.text,
                            "match_type": row.campaign_criterion.keyword.match_type.name,
                            "campaign_id": str(row.campaign.id),
                            "campaign_name": row.campaign.name,
                        }
                    )
        except GoogleAdsException as ex:
            print(f"Error fetching negative keywords for {customer_id}: {ex}")
        return rows

    # ============================================
    # WRITE OPERATIONS - Campaigns & Budgets
    # ============================================

    def create_campaign_budget(
        self,
        customer_id,
        name,
        amount_micros,
        explicitly_shared=True,
        validate_only=True,
    ):
        """
        Create a campaign budget.
        """
        campaign_budget_service = self.client.get_service("CampaignBudgetService")
        operation = self.client.get_type("CampaignBudgetOperation")
        campaign_budget = operation.create

        campaign_budget.name = name
        campaign_budget.amount_micros = amount_micros
        campaign_budget.delivery_method = (
            self.client.enums.BudgetDeliveryMethodEnum.STANDARD
        )
        campaign_budget.explicitly_shared = explicitly_shared

        try:
            request = self.client.get_type("MutateCampaignBudgetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = campaign_budget_service.mutate_campaign_budgets(request=request)

            if validate_only:
                print(f"Dry run successful: Budget '{name}' would be created.")
                return {"success": True, "dry_run": True}

            resource_name = response.results[0].resource_name
            print(f"Created campaign budget: {resource_name}")
            return {"success": True, "resource": resource_name, "dry_run": False}

        except GoogleAdsException as ex:
            print(f"Error creating budget: {ex}")
            return {"success": False, "error": str(ex)}

    def create_campaign(
        self,
        customer_id,
        budget_resource,
        name,
        advertising_channel_type="SEARCH",
        status="PAUSED",
        bidding_strategy_type="MANUAL_CPC",
        target_cpa_micros=None,
        target_roas=None,
        validate_only=True,
    ):
        """
        Create a new campaign with support for Smart Bidding.
        """
        campaign_service = self.client.get_service("CampaignService")
        operation = self.client.get_type("CampaignOperation")

        campaign = operation.create

        campaign.name = name
        campaign.advertising_channel_type = getattr(
            self.client.enums.AdvertisingChannelTypeEnum, advertising_channel_type
        )
        campaign.status = getattr(self.client.enums.CampaignStatusEnum, status)
        campaign.campaign_budget = budget_resource

        # Required for EEA (v22+)
        try:
            campaign.contains_eu_political_advertising = (
                self.client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
            )
        except AttributeError:
            print(
                "Warning: 'contains_eu_political_advertising' field not found in client library."
            )

        # Set Network Settings (Required for Search)
        if advertising_channel_type == "SEARCH":
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = True
            campaign.network_settings.target_content_network = False
            campaign.network_settings.target_partner_search_network = False

        # Set Bidding Strategy
        campaign.bidding_strategy_type = getattr(
            self.client.enums.BiddingStrategyTypeEnum, bidding_strategy_type
        )

        if bidding_strategy_type == "MANUAL_CPC":
            campaign.manual_cpc = self.client.get_type("ManualCpc")
            campaign.manual_cpc.enhanced_cpc_enabled = False
        elif bidding_strategy_type == "MAXIMIZE_CONVERSIONS":
            campaign.maximize_conversions = self.client.get_type("MaximizeConversions")
            if target_cpa_micros:
                campaign.maximize_conversions.target_cpa_micros = target_cpa_micros
        elif bidding_strategy_type == "TARGET_CPA":
            campaign.target_cpa = self.client.get_type("TargetCpa")
            if target_cpa_micros:
                campaign.target_cpa.target_cpa_micros = target_cpa_micros
        elif bidding_strategy_type == "MAXIMIZE_CONVERSION_VALUE":
            campaign.maximize_conversion_value = self.client.get_type(
                "MaximizeConversionValue"
            )
            if target_roas:
                campaign.maximize_conversion_value.target_roas = target_roas
        elif bidding_strategy_type == "TARGET_ROAS":
            campaign.target_roas = self.client.get_type("TargetRoas")
            if target_roas:
                campaign.target_roas.target_roas = target_roas

        try:
            request = self.client.get_type("MutateCampaignsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = campaign_service.mutate_campaigns(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Campaign '{name}' would be created with {bidding_strategy_type}."
                )
                return {"success": True, "dry_run": True}

            print(f"Created campaign: {response.results[0].resource_name}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error creating campaign: {ex}")
            return {"success": False, "error": str(ex)}

    def update_campaign_status(
        self, customer_id, campaign_id, status, validate_only=True
    ):
        """
        Update campaign status (ENABLED/PAUSED).
        """
        campaign_service = self.client.get_service("CampaignService")
        operation = self.client.get_type("CampaignOperation")

        campaign = operation.update
        campaign.resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"
        campaign.status = getattr(self.client.enums.CampaignStatusEnum, status)

        self.client.copy_from(
            operation.update_mask, protobuf_helpers.field_mask(None, campaign._pb)
        )

        try:
            request = self.client.get_type("MutateCampaignsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = campaign_service.mutate_campaigns(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Campaign {campaign_id} status would be updated to {status}."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated campaign {campaign_id} status to {status}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating campaign status: {ex}")
            return {"success": False, "error": str(ex)}

    def update_campaign_budget(
        self, customer_id, campaign_id, new_amount_micros, validate_only=True
    ):
        """
        Update the budget amount for a campaign.
        """
        query = f"""
            SELECT campaign.campaign_budget 
            FROM campaign 
            WHERE campaign.id = {campaign_id}
        """
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            budget_resource = None
            for batch in response:
                for row in batch.results:
                    budget_resource = row.campaign.campaign_budget
                    break

            if not budget_resource:
                return {
                    "success": False,
                    "error": "Campaign not found or no budget assigned.",
                }

            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            operation = self.client.get_type("CampaignBudgetOperation")
            budget = operation.update
            budget.resource_name = budget_resource
            budget.amount_micros = new_amount_micros

            self.client.copy_from(
                operation.update_mask, protobuf_helpers.field_mask(None, budget._pb)
            )

            request = self.client.get_type("MutateCampaignBudgetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = campaign_budget_service.mutate_campaign_budgets(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Budget for campaign {campaign_id} would be updated to {new_amount_micros}."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated budget for campaign {campaign_id}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating campaign budget: {ex}")
            return {"success": False, "error": str(ex)}

    def get_audience_performance(self, customer_id, date_range="LAST_30_DAYS"):
        """
        Fetches audience performance (Campaign Audience View).
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign_criterion.criterion_id,
                campaign_criterion.display_name,
                campaign_criterion.type,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign_audience_view
            WHERE segments.date DURING {date_range}
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            data = []
            for batch in response:
                for row in batch.results:
                    data.append(
                        {
                            "campaign_id": row.campaign.id,
                            "campaign_name": row.campaign.name,
                            "criterion_id": row.campaign_criterion.criterion_id,
                            "audience_name": row.campaign_criterion.display_name,
                            "type": row.campaign_criterion.type_.name,
                            "impressions": row.metrics.impressions,
                            "clicks": row.metrics.clicks,
                            "cost_micros": row.metrics.cost_micros,
                            "conversions": row.metrics.conversions,
                            "ctr": row.metrics.ctr,
                            "average_cpc": row.metrics.average_cpc,
                        }
                    )
            return pd.DataFrame(data)
        except GoogleAdsException as ex:
            print(f"Error fetching audience performance: {ex}")
            return pd.DataFrame()

    def attach_audience(
        self,
        customer_id,
        audience_resource_name,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Attach an audience (UserList, CustomSegment, etc.) to a Campaign or Ad Group.
        """
        if not campaign_id and not ad_group_id:
            return {
                "success": False,
                "error": "Must provide either campaign_id or ad_group_id",
            }

        operations = []

        if campaign_id:
            service_name = "CampaignCriterionService"
            request_type = "MutateCampaignCriteriaRequest"
            operation_type = "CampaignCriterionOperation"

            operation = self.client.get_type(operation_type)
            criterion = operation.create
            criterion.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
            criterion.user_list.user_list = (
                audience_resource_name  # Assuming UserList for now, could be others
            )
            # Note: For Custom Segments or Affinity, the field might be different (e.g. custom_affinity, etc.)
            # But "user_list" is the most common for remarketing.
            # If audience_resource_name is a user list resource.

            operations.append(operation)

        elif ad_group_id:
            service_name = "AdGroupCriterionService"
            request_type = "MutateAdGroupCriteriaRequest"
            operation_type = "AdGroupCriterionOperation"

            operation = self.client.get_type(operation_type)
            criterion = operation.create
            criterion.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
            criterion.user_list.user_list = audience_resource_name

            operations.append(operation)

        service = self.client.get_service(service_name)

        try:
            request = self.client.get_type(request_type)
            request.customer_id = customer_id
            request.operations = operations
            request.validate_only = validate_only

            response = getattr(
                service, f"mutate_{service_name[0].lower() + service_name[1:-7]}a"
            )(request=request)

            if validate_only:
                print(f"Dry run successful: Audience would be attached.")
                return {"success": True, "dry_run": True}

            print(f"Attached audience: {response.results[0].resource_name}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error attaching audience: {ex}")
            return {"success": False, "error": str(ex)}

    # ============================================
    # WRITE OPERATIONS - Ad Groups
    # ============================================

    def remove_campaign(self, customer_id, campaign_id, validate_only=True):
        """
        Remove (cancel) a campaign.
        """
        campaign_service = self.client.get_service("CampaignService")
        operation = self.client.get_type("CampaignOperation")

        operation.remove = f"customers/{customer_id}/campaigns/{campaign_id}"

        try:
            request = self.client.get_type("MutateCampaignsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = campaign_service.mutate_campaigns(request=request)

            if validate_only:
                print(f"Dry run successful: Campaign {campaign_id} would be removed.")
                return {"success": True, "dry_run": True}

            print(f"Removed campaign {campaign_id}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error removing campaign: {ex}")
            return {"success": False, "error": str(ex)}

    def create_label(self, customer_id, name, validate_only=True):
        """
        Create a new label.
        """
        label_service = self.client.get_service("LabelService")
        operation = self.client.get_type("LabelOperation")

        label = operation.create
        label.name = name
        # label.text_label.background_color = "#FFFFFF" # Optional
        # label.text_label.description = "Created by Monday Brew AI"

        try:
            request = self.client.get_type("MutateLabelsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = label_service.mutate_labels(request=request)

            if validate_only:
                print(f"Dry run successful: Label '{name}' would be created.")
                return {"success": True, "dry_run": True}

            print(f"Created label: {response.results[0].resource_name}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error creating label: {ex}")
            return {"success": False, "error": str(ex)}

    def apply_label(
        self, customer_id, resource_name, label_resource_name, validate_only=True
    ):
        """
        Apply a label to a resource (Campaign, AdGroup, AdGroupCriterion, AdGroupAd).
        """
        # Determine service based on resource type
        if "campaigns" in resource_name:
            service_name = "CampaignLabelService"
            operation_type = "CampaignLabelOperation"
            request_type = "MutateCampaignLabelsRequest"
            entity_field = "campaign"
        elif "adGroups" in resource_name:
            service_name = "AdGroupLabelService"
            operation_type = "AdGroupLabelOperation"
            request_type = "MutateAdGroupLabelsRequest"
            entity_field = "ad_group"
        elif "adGroupCriteria" in resource_name:
            service_name = "AdGroupCriterionLabelService"
            operation_type = "AdGroupCriterionLabelOperation"
            request_type = "MutateAdGroupCriterionLabelsRequest"
            entity_field = "ad_group_criterion"
        elif "adGroupAds" in resource_name:
            service_name = "AdGroupAdLabelService"
            operation_type = "AdGroupAdLabelOperation"
            request_type = "MutateAdGroupAdLabelsRequest"
            entity_field = "ad_group_ad"
        else:
            return {"success": False, "error": "Unsupported resource type for labeling"}

        service = self.client.get_service(service_name)
        operation = self.client.get_type(operation_type)

        # Create the relationship object (e.g., CampaignLabel)
        relationship = operation.create
        setattr(relationship, entity_field, resource_name)
        relationship.label = label_resource_name

        try:
            request = self.client.get_type(request_type)
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            # Construct method name: mutate_campaign_labels, mutate_ad_group_labels, etc.
            # Service name format: XxxLabelService -> mutate_xxx_labels
            # We can use the entity_field which is already snake_case (e.g. campaign, ad_group)
            # But entity_field is singular. We need plural.
            # Let's map explicitly or use a better conversion.

            method_name_map = {
                "CampaignLabelService": "mutate_campaign_labels",
                "AdGroupLabelService": "mutate_ad_group_labels",
                "AdGroupCriterionLabelService": "mutate_ad_group_criterion_labels",
                "AdGroupAdLabelService": "mutate_ad_group_ad_labels",
            }
            method_name = method_name_map.get(service_name)

            response = getattr(service, method_name)(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Label {label_resource_name} would be applied to {resource_name}."
                )
                return {"success": True, "dry_run": True}

            print(f"Applied label to {resource_name}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error applying label: {ex}")
            return {"success": False, "error": str(ex)}

    def create_ad_group(
        self,
        customer_id,
        campaign_id,
        name,
        cpc_bid_micros=1000000,
        status="PAUSED",
        validate_only=True,
    ):
        """
        Create a new ad group.
        """
        ad_group_service = self.client.get_service("AdGroupService")
        operation = self.client.get_type("AdGroupOperation")
        ad_group = operation.create

        ad_group.name = name
        ad_group.status = getattr(self.client.enums.AdGroupStatusEnum, status)
        ad_group.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
        ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = cpc_bid_micros

        try:
            request = self.client.get_type("MutateAdGroupsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_service.mutate_ad_groups(request=request)

            if validate_only:
                print(f"Dry run successful: Ad Group '{name}' would be created.")
                return {"success": True, "dry_run": True}

            resource_name = response.results[0].resource_name
            print(f"Created ad group: {resource_name}")
            return {"success": True, "resource": resource_name, "dry_run": False}

        except GoogleAdsException as ex:
            print(f"Error creating ad group: {ex}")
            return {"success": False, "error": str(ex)}

    def update_ad_group_status(
        self, customer_id, ad_group_id, status, validate_only=True
    ):
        """
        Update ad group status (ENABLED/PAUSED).
        """
        ad_group_service = self.client.get_service("AdGroupService")
        operation = self.client.get_type("AdGroupOperation")

        ad_group = operation.update
        ad_group.resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"
        ad_group.status = getattr(self.client.enums.AdGroupStatusEnum, status)

        self.client.copy_from(
            operation.update_mask, protobuf_helpers.field_mask(None, ad_group._pb)
        )

        try:
            request = self.client.get_type("MutateAdGroupsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_service.mutate_ad_groups(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Ad Group {ad_group_id} status would be updated to {status}."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated ad group {ad_group_id} status to {status}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating ad group status: {ex}")
            return {"success": False, "error": str(ex)}

    def update_ad_group_bids(
        self, customer_id, ad_group_id, cpc_bid_micros, validate_only=True
    ):
        """
        Update ad group default CPC bid.
        """
        ad_group_service = self.client.get_service("AdGroupService")
        operation = self.client.get_type("AdGroupOperation")

        ad_group = operation.update
        ad_group.resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"
        ad_group.cpc_bid_micros = cpc_bid_micros

        self.client.copy_from(
            operation.update_mask, protobuf_helpers.field_mask(None, ad_group._pb)
        )

        try:
            request = self.client.get_type("MutateAdGroupsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_service.mutate_ad_groups(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Ad Group {ad_group_id} bid would be updated to {cpc_bid_micros}."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated ad group {ad_group_id} bid")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating ad group bid: {ex}")
            return {"success": False, "error": str(ex)}

    # ============================================
    # WRITE OPERATIONS - Keywords
    # ============================================

    def add_keywords(
        self,
        customer_id,
        ad_group_id,
        keywords,
        match_type="PHRASE",
        cpc_bid_micros=None,
        validate_only=True,
    ):
        """
        Add positive keywords to an ad group.
        """
        ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")

        operations = []
        for keyword_text in keywords:
            operation = self.client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
            criterion.status = self.client.enums.AdGroupCriterionStatusEnum.ENABLED
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = getattr(
                self.client.enums.KeywordMatchTypeEnum, match_type
            )

            if cpc_bid_micros:
                criterion.cpc_bid_micros = cpc_bid_micros

            operations.append(operation)

        try:
            request = self.client.get_type("MutateAdGroupCriteriaRequest")
            request.customer_id = customer_id
            request.operations = operations
            request.validate_only = validate_only

            response = ad_group_criterion_service.mutate_ad_group_criteria(
                request=request
            )

            if validate_only:
                print(f"Dry run successful: {len(keywords)} keywords would be added.")
                return {"success": True, "dry_run": True}

            added_resources = [res.resource_name for res in response.results]
            print(f"Added {len(added_resources)} keywords to ad group {ad_group_id}")
            return {"success": True, "resources": added_resources, "dry_run": False}

        except GoogleAdsException as ex:
            print(f"Error adding keywords: {ex}")
            return {"success": False, "error": str(ex)}

    def update_keyword_bids(
        self, customer_id, criterion_id, cpc_bid_micros, validate_only=True
    ):
        """
        Update bid for a specific keyword.
        """
        ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
        operation = self.client.get_type("AdGroupCriterionOperation")

        criterion = operation.update
        criterion.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{criterion_id}"
        )
        criterion.cpc_bid_micros = cpc_bid_micros

        self.client.copy_from(
            operation.update_mask, protobuf_helpers.field_mask(None, criterion._pb)
        )

        try:
            request = self.client.get_type("MutateAdGroupCriteriaRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_criterion_service.mutate_ad_group_criteria(
                request=request
            )

            if validate_only:
                print(
                    f"Dry run successful: Keyword bid for {criterion_id} would be updated."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated keyword bid for {criterion_id}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating keyword bid: {ex}")
            return {"success": False, "error": str(ex)}

    def remove_keyword(self, customer_id, criterion_id, validate_only=True):
        """
        Remove (actually pause/remove) a keyword.
        """
        ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
        operation = self.client.get_type("AdGroupCriterionOperation")

        operation.remove = f"customers/{customer_id}/adGroupCriteria/{criterion_id}"

        try:
            request = self.client.get_type("MutateAdGroupCriteriaRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_criterion_service.mutate_ad_group_criteria(
                request=request
            )

            if validate_only:
                print(f"Dry run successful: Keyword {criterion_id} would be removed.")
                return {"success": True, "dry_run": True}

            print(f"Removed keyword {criterion_id}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error removing keyword: {ex}")
            return {"success": False, "error": str(ex)}

    # ============================================
    # WRITE OPERATIONS - Ads
    # ============================================

    def create_responsive_search_ad(
        self,
        customer_id,
        ad_group_id,
        headlines,
        descriptions,
        final_urls,
        path1=None,
        path2=None,
        validate_only=True,
    ):
        """
        Create a Responsive Search Ad (RSA).
        headlines: list of strings OR list of dicts {'text': '...', 'pinned_field': 'HEADLINE_1'}
        descriptions: list of strings OR list of dicts {'text': '...', 'pinned_field': 'DESCRIPTION_1'}
        """
        ad_group_ad_service = self.client.get_service("AdGroupAdService")
        operation = self.client.get_type("AdGroupAdOperation")

        ad_group_ad = operation.create
        ad_group_ad.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
        ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.ENABLED

        ad_group_ad.ad.final_urls.extend(final_urls)

        if path1:
            ad_group_ad.ad.responsive_search_ad.path1 = path1
        if path2:
            ad_group_ad.ad.responsive_search_ad.path2 = path2

        # Helper to process assets
        def process_assets(assets, asset_type):
            processed = []
            for item in assets:
                asset = self.client.get_type("AdTextAsset")
                if isinstance(item, dict):
                    asset.text = item["text"]
                    if "pinned_field" in item and item["pinned_field"]:
                        # Map string to enum if needed, or assume valid enum name
                        # e.g. HEADLINE_1, DESCRIPTION_1
                        pinned_enum = getattr(
                            self.client.enums.ServedAssetFieldTypeEnum,
                            item["pinned_field"],
                            None,
                        )
                        if pinned_enum:
                            asset.pinned_field = pinned_enum
                else:
                    asset.text = item
                processed.append(asset)
            return processed

        ad_group_ad.ad.responsive_search_ad.headlines.extend(
            process_assets(headlines, "HEADLINE")
        )
        ad_group_ad.ad.responsive_search_ad.descriptions.extend(
            process_assets(descriptions, "DESCRIPTION")
        )

        try:
            request = self.client.get_type("MutateAdGroupAdsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_ad_service.mutate_ad_group_ads(request=request)

            if validate_only:
                print(
                    f"Dry run successful: RSA would be created in Ad Group {ad_group_id}."
                )
                return {"success": True, "dry_run": True}

            print(f"Created RSA: {response.results[0].resource_name}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error creating RSA: {ex}")
            return {"success": False, "error": str(ex)}

    def update_ad_status(self, customer_id, ad_id, status, validate_only=True):
        """
        Update ad status (ENABLED/PAUSED).
        """
        # Note: We need the ad_group_id to construct the resource name for AdGroupAd.
        # Resource name format: customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}
        # Since we only have ad_id, we might need to search for it first or ask caller for ad_group_id.
        # For now, let's assume the caller passes the full resource name or we search.
        # Let's search for the ad to get the resource name.

        query = f"""
            SELECT ad_group_ad.resource_name 
            FROM ad_group_ad 
            WHERE ad_group_ad.ad.id = {ad_id}
        """
        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id, query=query
            )
            resource_name = None
            for batch in response:
                for row in batch.results:
                    resource_name = row.ad_group_ad.resource_name
                    break

            if not resource_name:
                return {"success": False, "error": f"Ad {ad_id} not found."}

            ad_group_ad_service = self.client.get_service("AdGroupAdService")
            operation = self.client.get_type("AdGroupAdOperation")

            ad = operation.update
            ad.resource_name = resource_name
            ad.status = getattr(self.client.enums.AdGroupAdStatusEnum, status)

            self.client.copy_from(
                operation.update_mask, protobuf_helpers.field_mask(None, ad._pb)
            )

            request = self.client.get_type("MutateAdGroupAdsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = ad_group_ad_service.mutate_ad_group_ads(request=request)

            if validate_only:
                print(
                    f"Dry run successful: Ad {ad_id} status would be updated to {status}."
                )
                return {"success": True, "dry_run": True}

            print(f"Updated ad {ad_id} status to {status}")
            return {
                "success": True,
                "resource": response.results[0].resource_name,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error updating ad status: {ex}")
            return {"success": False, "error": str(ex)}

    # ============================================
    # WRITE OPERATIONS - Conversions
    # ============================================

    def upload_offline_conversions(self, customer_id, conversions, validate_only=True):
        """
        Upload offline click conversions.
        conversions: list of dicts with 'gclid', 'conversion_action', 'conversion_date_time', 'conversion_value'
        """
        conversion_upload_service = self.client.get_service("ConversionUploadService")

        click_conversions = []
        for conv in conversions:
            click_conversion = self.client.get_type("ClickConversion")
            click_conversion.gclid = conv["gclid"]
            click_conversion.conversion_action = conv[
                "conversion_action"
            ]  # Resource name or just ID? Resource name usually.
            click_conversion.conversion_date_time = conv["conversion_date_time"]
            if "conversion_value" in conv:
                click_conversion.conversion_value = float(conv["conversion_value"])
            if "currency_code" in conv:
                click_conversion.currency_code = conv["currency_code"]
            click_conversions.append(click_conversion)

        try:
            request = self.client.get_type("UploadClickConversionsRequest")
            request.customer_id = customer_id
            request.conversions = click_conversions
            request.validate_only = validate_only

            response = conversion_upload_service.upload_click_conversions(
                request=request
            )

            if validate_only:
                print(
                    f"Dry run successful: {len(conversions)} conversions would be uploaded."
                )
                return {"success": True, "dry_run": True}

            # Check for partial failures
            if response.partial_failure_error:
                print(
                    f"Partial failure occurred: {response.partial_failure_error.message}"
                )

            uploaded_count = len(response.results)
            print(f"Uploaded {uploaded_count} conversions.")
            return {
                "success": True,
                "uploaded_count": uploaded_count,
                "results": response.results,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error uploading conversions: {ex}")
            return {"success": False, "error": str(ex)}

    # ============================================
    # WRITE OPERATIONS - Assets
    # ============================================

    def upload_image_asset(self, customer_id, image_bytes, name, validate_only=True):
        """
        Upload an image asset.
        """
        asset_service = self.client.get_service("AssetService")
        operation = self.client.get_type("AssetOperation")
        asset = operation.create

        asset.name = name
        asset.type_ = self.client.enums.AssetTypeEnum.IMAGE
        asset.image_asset.data = image_bytes

        try:
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(f"Dry run successful: Image asset '{name}' would be uploaded.")
                return {"success": True, "dry_run": True}

            resource_name = response.results[0].resource_name
            print(f"Uploaded image asset: {resource_name}")
            return {"success": True, "resource": resource_name, "dry_run": False}

        except GoogleAdsException as ex:
            print(f"Error uploading image asset: {ex}")
            return {"success": False, "error": str(ex)}

    def create_sitelink_extension(
        self, customer_id, campaign_id, sitelinks, validate_only=True
    ):
        """
        Create sitelink assets and attach them to a campaign.
        sitelinks: list of dicts with 'text', 'description1', 'description2', 'final_urls'
        """
        # 1. Create Assets
        asset_service = self.client.get_service("AssetService")
        asset_operations = []

        for sl in sitelinks:
            operation = self.client.get_type("AssetOperation")
            asset = operation.create
            asset.type_ = self.client.enums.AssetTypeEnum.SITELINK
            asset.sitelink_asset.link_text = sl["text"]
            if "description1" in sl:
                asset.sitelink_asset.description1 = sl["description1"]
            if "description2" in sl:
                asset.sitelink_asset.description2 = sl["description2"]
            asset.final_urls.extend(sl["final_urls"])
            asset_operations.append(operation)

        try:
            # Create assets first
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = asset_operations
            request.validate_only = validate_only

            asset_response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(
                    f"Dry run successful: {len(sitelinks)} sitelink assets would be created."
                )
                return {"success": True, "dry_run": True}

            asset_resource_names = [res.resource_name for res in asset_response.results]

            # 2. Attach to Campaign
            campaign_asset_service = self.client.get_service("CampaignAssetService")
            camp_asset_operations = []

            for resource_name in asset_resource_names:
                operation = self.client.get_type("CampaignAssetOperation")
                camp_asset = operation.create
                camp_asset.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
                camp_asset.asset = resource_name
                camp_asset.field_type = self.client.enums.AssetFieldTypeEnum.SITELINK
                camp_asset_operations.append(operation)

            request = self.client.get_type("MutateCampaignAssetsRequest")
            request.customer_id = customer_id
            request.operations = camp_asset_operations

            campaign_asset_service.mutate_campaign_assets(request=request)

            print(
                f"Attached {len(asset_resource_names)} sitelinks to campaign {campaign_id}"
            )
            return {
                "success": True,
                "resources": asset_resource_names,
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error creating sitelinks: {ex}")
            return {"success": False, "error": str(ex)}

    def create_callout_assets(
        self,
        customer_id,
        callout_texts,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Create Callout Assets and attach them to a Campaign or Ad Group.
        """
        if not campaign_id and not ad_group_id:
            return {
                "success": False,
                "error": "Must provide either campaign_id or ad_group_id",
            }

        asset_service = self.client.get_service("AssetService")
        operations = []

        for text in callout_texts:
            operation = self.client.get_type("AssetOperation")
            asset = operation.create
            asset.callout_asset.callout_text = text
            operations.append(operation)

        try:
            # 1. Create Assets
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = operations
            request.validate_only = validate_only

            response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(
                    f"Dry run successful: {len(callout_texts)} Callout Assets would be created."
                )
                return {"success": True, "dry_run": True}

            asset_resource_names = [res.resource_name for res in response.results]
            print(f"Created {len(asset_resource_names)} Callout Assets.")

            # 2. Attach Assets
            return self._attach_assets(
                customer_id,
                asset_resource_names,
                "CALLOUT",
                campaign_id,
                ad_group_id,
                validate_only,
            )

        except GoogleAdsException as ex:
            print(f"Error creating callout assets: {ex}")
            return {"success": False, "error": str(ex)}

    def create_structured_snippet_assets(
        self,
        customer_id,
        header,
        values,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Create Structured Snippet Assets and attach them.
        """
        if not campaign_id and not ad_group_id:
            return {
                "success": False,
                "error": "Must provide either campaign_id or ad_group_id",
            }

        asset_service = self.client.get_service("AssetService")
        operation = self.client.get_type("AssetOperation")
        asset = operation.create

        asset.structured_snippet_asset.header = header
        asset.structured_snippet_asset.values = values

        try:
            # 1. Create Asset
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(f"Dry run successful: Structured Snippet Asset would be created.")
                return {"success": True, "dry_run": True}

            asset_resource_name = response.results[0].resource_name
            print(f"Created Structured Snippet Asset: {asset_resource_name}")

            # 2. Attach Asset
            return self._attach_assets(
                customer_id,
                [asset_resource_name],
                "STRUCTURED_SNIPPET",
                campaign_id,
                ad_group_id,
                validate_only,
            )

        except GoogleAdsException as ex:
            print(f"Error creating structured snippet asset: {ex}")
            return {"success": False, "error": str(ex)}

    def create_call_assets(
        self,
        customer_id,
        phone_number,
        country_code,
        conversion_action_id=None,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Create Call Asset and attach it.
        """
        if not campaign_id and not ad_group_id:
            return {
                "success": False,
                "error": "Must provide either campaign_id or ad_group_id",
            }

        asset_service = self.client.get_service("AssetService")
        operation = self.client.get_type("AssetOperation")
        asset = operation.create

        asset.call_asset.country_code = country_code
        asset.call_asset.phone_number = phone_number
        asset.call_asset.call_conversion_reporting_state = (
            self.client.enums.CallConversionReportingStateEnum.USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION
        )

        if conversion_action_id:
            asset.call_asset.call_conversion_action = (
                f"customers/{customer_id}/conversionActions/{conversion_action_id}"
            )

        try:
            # 1. Create Asset
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(f"Dry run successful: Call Asset would be created.")
                return {"success": True, "dry_run": True}

            asset_resource_name = response.results[0].resource_name
            print(f"Created Call Asset: {asset_resource_name}")

            # 2. Attach Asset
            return self._attach_assets(
                customer_id,
                [asset_resource_name],
                "CALL",
                campaign_id,
                ad_group_id,
                validate_only,
            )

        except GoogleAdsException as ex:
            print(f"Error creating call asset: {ex}")
            return {"success": False, "error": str(ex)}

    def create_lead_form_assets(
        self,
        customer_id,
        business_name,
        headline,
        description,
        fields,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Create Lead Form Asset and attach it.
        fields: list of enums (e.g., "FULL_NAME", "EMAIL", "PHONE_NUMBER")
        """
        if not campaign_id and not ad_group_id:
            return {
                "success": False,
                "error": "Must provide either campaign_id or ad_group_id",
            }

        asset_service = self.client.get_service("AssetService")
        operation = self.client.get_type("AssetOperation")
        asset = operation.create

        asset.lead_form_asset.business_name = business_name
        asset.lead_form_asset.headline = headline
        asset.lead_form_asset.description = description

        # Add fields
        for field in fields:
            form_field = self.client.get_type("LeadFormField")
            form_field.input_type = getattr(
                self.client.enums.LeadFormFieldUserInputTypeEnum, field
            )
            asset.lead_form_asset.fields.append(form_field)

        try:
            # 1. Create Asset
            request = self.client.get_type("MutateAssetsRequest")
            request.customer_id = customer_id
            request.operations = [operation]
            request.validate_only = validate_only

            response = asset_service.mutate_assets(request=request)

            if validate_only:
                print(f"Dry run successful: Lead Form Asset would be created.")
                return {"success": True, "dry_run": True}

            asset_resource_name = response.results[0].resource_name
            print(f"Created Lead Form Asset: {asset_resource_name}")

            # 2. Attach Asset
            return self._attach_assets(
                customer_id,
                [asset_resource_name],
                "LEAD_FORM",
                campaign_id,
                ad_group_id,
                validate_only,
            )

        except GoogleAdsException as ex:
            print(f"Error creating lead form asset: {ex}")
            return {"success": False, "error": str(ex)}

    def _attach_assets(
        self,
        customer_id,
        asset_resource_names,
        field_type,
        campaign_id=None,
        ad_group_id=None,
        validate_only=True,
    ):
        """
        Helper to attach assets to Campaign or AdGroup.
        """
        operations = []

        if campaign_id:
            service_name = "CampaignAssetService"
            request_type = "MutateCampaignAssetsRequest"

            for asset_resource in asset_resource_names:
                operation = self.client.get_type("CampaignAssetOperation")
                link = operation.create
                link.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
                link.asset = asset_resource
                link.field_type = getattr(
                    self.client.enums.AssetFieldTypeEnum, field_type
                )
                operations.append(operation)

        elif ad_group_id:
            service_name = "AdGroupAssetService"
            request_type = "MutateAdGroupAssetsRequest"

            for asset_resource in asset_resource_names:
                operation = self.client.get_type("AdGroupAssetOperation")
                link = operation.create
                link.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
                link.asset = asset_resource
                link.field_type = getattr(
                    self.client.enums.AssetFieldTypeEnum, field_type
                )
                operations.append(operation)

        service = self.client.get_service(service_name)

        # Construct method name: mutate_campaign_assets, mutate_ad_group_assets
        method_name_map = {
            "CampaignAssetService": "mutate_campaign_assets",
            "AdGroupAssetService": "mutate_ad_group_assets",
        }
        method_name = method_name_map.get(service_name)

        try:
            request = self.client.get_type(request_type)
            request.customer_id = customer_id
            request.operations = operations
            request.validate_only = validate_only

            response = getattr(service, method_name)(request=request)

            if validate_only:
                print(f"Dry run successful: Assets would be attached.")
                return {"success": True, "dry_run": True}

            print(f"Attached {len(response.results)} assets.")
            return {
                "success": True,
                "resources": [res.resource_name for res in response.results],
                "dry_run": False,
            }

        except GoogleAdsException as ex:
            print(f"Error attaching assets: {ex}")
            return {"success": False, "error": str(ex)}
