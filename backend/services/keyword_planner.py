from google.ads.googleads.client import GoogleAdsClient
import os
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env (or local .env fallback)
ensure_credentials()


class KeywordPlannerService:
    def __init__(self):
        # Initialize Google Ads Client
        self.client = GoogleAdsClient.load_from_dict(
            {
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
                "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
                "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
                "use_proto_plus": True,
            }
        )

        # Default customer ID for planning (can be overridden in methods)
        # If not set in env, it will need to be passed to methods
        self.customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    def _lookup_location_id(self, location_name):
        """
        Searches for a location ID by name using the GeoTargetConstantService.
        Prioritizes 'Country' target types.
        """
        gtc_service = self.client.get_service("GeoTargetConstantService")
        request = self.client.get_type("SuggestGeoTargetConstantsRequest")
        request.locale = "en"
        request.location_names.names.append(location_name)

        try:
            response = gtc_service.suggest_geo_target_constants(request=request)

            # Prioritize Country > Region > City
            best_match = None
            for suggestion in response.geo_target_constant_suggestions:
                geo = suggestion.geo_target_constant

                # Exact match preference
                if geo.name.lower() == location_name.lower():
                    if geo.target_type == "Country":
                        return geo.resource_name
                    best_match = geo.resource_name

            # If no exact country match, take the first result (usually the most relevant)
            if not best_match and response.geo_target_constant_suggestions:
                return response.geo_target_constant_suggestions[
                    0
                ].geo_target_constant.resource_name

            return best_match

        except Exception as e:
            print(f"Error looking up location '{location_name}': {e}")
            return None

    def generate_keyword_ideas(
        self,
        keywords=None,
        page_url=None,
        location_ids=None,
        language_id="1000",
        customer_id=None,
    ):
        """
        Generates keyword ideas based on a list of seed keywords OR a page URL.
        """
        keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")

        # 1. Configure Request
        request = self.client.get_type("GenerateKeywordIdeasRequest")

        # Use passed ID, or instance ID, or error
        target_customer_id = customer_id or self.customer_id
        if not target_customer_id:
            raise ValueError(
                "customer_id must be provided either in init (env var GOOGLE_ADS_CUSTOMER_ID) or as an argument."
            )

        request.customer_id = target_customer_id
        request.language = f"languageConstants/{language_id}"

        # Handle Location Logic
        final_location_ids = []

        if location_ids:
            for loc in location_ids:
                # Check if it's already a resource name
                if "geoTargetConstants/" in str(loc):
                    final_location_ids.append(str(loc))
                    continue

                # Check if it's a numeric ID
                if str(loc).isdigit():
                    final_location_ids.append(f"geoTargetConstants/{loc}")
                    continue

                # Dynamic Lookup
                found_resource = self._lookup_location_id(loc)
                if found_resource:
                    final_location_ids.append(found_resource)
                else:
                    print(
                        f"Warning: Could not find location '{loc}'. Defaulting to USA."
                    )
                    final_location_ids.append("geoTargetConstants/2840")
        else:
            # Default to USA
            final_location_ids.append("geoTargetConstants/2840")

        request.geo_target_constants.extend(final_location_ids)

        request.include_adult_keywords = False
        request.keyword_plan_network = (
            self.client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        )

        # Set Seed (Keywords OR URL)
        if page_url:
            request.url_seed.url = page_url
            print(f"--- Generating Ideas for URL: {page_url} ---")
        elif keywords:
            request.keyword_seed.keywords.extend(keywords)
            print(f"--- Generating Ideas for Keywords: {keywords} ---")
        else:
            raise ValueError("Must provide either 'keywords' or 'page_url'.")

        try:
            # 2. Execute Request
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

            # 3. Parse Results
            ideas = []
            for idea in response:
                metrics = idea.keyword_idea_metrics
                ideas.append(
                    {
                        "text": idea.text,
                        "avg_monthly_searches": metrics.avg_monthly_searches,
                        "competition": metrics.competition.name,
                        "low_top_of_page_bid": metrics.low_top_of_page_bid_micros
                        / 1_000_000,
                        "high_top_of_page_bid": metrics.high_top_of_page_bid_micros
                        / 1_000_000,
                    }
                )

            # Sort by volume
            ideas.sort(key=lambda x: x["avg_monthly_searches"], reverse=True)
            return ideas[:20]  # Return top 20

        except Exception as e:
            print(f"Error generating keyword ideas: {e}")
            return []

    def get_forecast_metrics(self, keywords, location_id="Denmark", language_id="1000"):
        """
        Generates forecast metrics (Clicks, Cost, CPC) for a list of keywords.
        Creates a temporary Keyword Plan, generates metrics, and returns them.
        """
        print(f"--- Generating Forecast for: {keywords} in {location_id} ---")

        try:
            # Services
            kp_service = self.client.get_service("KeywordPlanService")
            kpc_service = self.client.get_service("KeywordPlanCampaignService")
            kpag_service = self.client.get_service("KeywordPlanAdGroupService")
            kpagk_service = self.client.get_service("KeywordPlanAdGroupKeywordService")

            # 1. Create Keyword Plan
            kp_operation = self.client.get_type("KeywordPlanOperation")
            keyword_plan = kp_operation.create
            keyword_plan.name = f"Forecast Plan {keywords[0]}..."
            keyword_plan.forecast_period.date_interval = (
                self.client.enums.KeywordPlanForecastIntervalEnum.NEXT_QUARTER
            )

            kp_response = kp_service.mutate_keyword_plans(
                customer_id=self.customer_id, operations=[kp_operation]
            )
            plan_resource = kp_response.results[0].resource_name

            # 2. Create Campaign
            kpc_operation = self.client.get_type("KeywordPlanCampaignOperation")
            campaign = kpc_operation.create
            campaign.name = "Forecast Campaign"
            campaign.keyword_plan = plan_resource
            campaign.cpc_bid_micros = 1000000  # Default €1 bid
            campaign.keyword_plan_network = (
                self.client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            )

            # Geo Target
            geo_resource = self._lookup_location_id(location_id)
            if geo_resource:
                campaign.geo_targets.append({"geo_target_constant": geo_resource})
            else:
                campaign.geo_targets.append(
                    {"geo_target_constant": "geoTargetConstants/2840"}
                )  # Default US

            # Language
            campaign.language_constants.append(f"languageConstants/{language_id}")

            kpc_response = kpc_service.mutate_keyword_plan_campaigns(
                customer_id=self.customer_id, operations=[kpc_operation]
            )
            campaign_resource = kpc_response.results[0].resource_name

            # 3. Create Ad Group
            kpag_operation = self.client.get_type("KeywordPlanAdGroupOperation")
            ad_group = kpag_operation.create
            ad_group.name = "Forecast Ad Group"
            ad_group.keyword_plan_campaign = campaign_resource

            kpag_response = kpag_service.mutate_keyword_plan_ad_groups(
                customer_id=self.customer_id, operations=[kpag_operation]
            )
            ad_group_resource = kpag_response.results[0].resource_name

            # 4. Add Keywords
            kpagk_operations = []
            for kw in keywords:
                op = self.client.get_type("KeywordPlanAdGroupKeywordOperation")
                kpagk = op.create
                kpagk.keyword_plan_ad_group = ad_group_resource
                kpagk.cpc_bid_micros = 2000000  # €2 max bid
                kpagk.match_type = self.client.enums.KeywordMatchTypeEnum.EXACT
                kpagk.text = kw
                kpagk_operations.append(op)

            kpagk_service.mutate_keyword_plan_ad_group_keywords(
                customer_id=self.customer_id, operations=kpagk_operations
            )

            # 5. Generate Forecast
            response = kp_service.generate_forecast_metrics(keyword_plan=plan_resource)

            # 6. Parse Results
            metrics = response.campaign_forecasts[0].campaign_forecast

            result = {
                "estimated_clicks": metrics.clicks,
                "estimated_impressions": metrics.impressions,
                "estimated_cost_micros": metrics.cost_micros,
                "estimated_cost": metrics.cost_micros / 1_000_000,
                "estimated_ctr": metrics.ctr,
                "estimated_avg_cpc": metrics.average_cpc / 1_000_000,
            }

            return result

        except Exception as e:
            print(f"Error generating forecast: {e}")
            return {"error": str(e)}

    def get_historical_metrics(
        self, keywords, location_id="Denmark", language_id="1000"
    ):
        """
        Generates historical metrics for a list of keywords using KeywordPlanIdeaService.
        """
        print(f"--- Generating Historical Metrics for: {keywords} in {location_id} ---")

        try:
            idea_service = self.client.get_service("KeywordPlanIdeaService")
            request = self.client.get_type("GenerateKeywordHistoricalMetricsRequest")

            request.customer_id = self.customer_id
            request.keywords = keywords
            request.geo_target_constants.append(
                self._lookup_location_id(location_id) or "geoTargetConstants/2840"
            )
            request.keyword_plan_network = (
                self.client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            )
            request.language = f"languageConstants/{language_id}"

            response = idea_service.generate_keyword_historical_metrics(request=request)

            results = []
            for result in response.results:
                metrics = result.keyword_metrics
                results.append(
                    {
                        "text": result.text,
                        "avg_monthly_searches": metrics.avg_monthly_searches,
                        "competition": metrics.competition.name,
                        "low_top_of_page_bid": metrics.low_top_of_page_bid_micros
                        / 1_000_000,
                        "high_top_of_page_bid": metrics.high_top_of_page_bid_micros
                        / 1_000_000,
                    }
                )

            return results

        except Exception as e:
            print(f"Error generating history: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv

    load_dotenv()
    service = KeywordPlannerService()
    results = service.generate_keyword_ideas(["wedding dress", "cheap wedding dress"])
    for r in results:
        print(r)
