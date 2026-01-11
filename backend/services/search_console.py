import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env (or local .env fallback)
ensure_credentials()


class SearchConsoleService:
    def __init__(self):
        # Re-use the OAuth credentials from Google Ads if possible,
        # assuming the user granted GSC scopes.
        # If not, we might need a separate auth flow, but for now we try to unify.

        # We construct credentials from the environment variables
        self.creds = Credentials(
            token=None,  # Access token (will be refreshed)
            refresh_token=os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_ADS_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        )

        self.service = build("searchconsole", "v1", credentials=self.creds)

    def _find_matching_site(self, url):
        """
        Finds the correct GSC property for a given URL.
        Handles 'sc-domain:' prefixes and protocol differences.
        """
        try:
            # 1. Get all accessible sites
            site_list = self.service.sites().list().execute()
            sites = [s["siteUrl"] for s in site_list.get("siteEntry", [])]

            # 2. Normalize Input
            # Remove http://, https://, www., and trailing slashes
            clean_input = (
                url.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
                .strip("/")
            )

            print(
                f"--- GSC Lookup: Searching for '{clean_input}' in {len(sites)} sites ---"
            )

            # 3. Search for Match
            for site in sites:
                # Normalize Site ID
                clean_site = (
                    site.replace("sc-domain:", "")
                    .replace("https://", "")
                    .replace("http://", "")
                    .replace("www.", "")
                    .strip("/")
                )

                if clean_site == clean_input:
                    print(f" -> Found Match: {site}")
                    return site

            print(f" -> No exact match found for {url}")
            return None

        except Exception as e:
            print(f"Error finding matching site: {e}")
            return None

    def get_organic_performance(self, site_url, days=30):
        """
        Fetches organic performance data (Clicks, Impressions, CTR, Position)
        for a specific site over the last N days.
        """
        # 1. Resolve the correct Property ID (e.g., sc-domain:example.com)
        actual_site_url = self._find_matching_site(site_url)

        if not actual_site_url:
            return {
                "error": f"Could not find GSC property for {site_url}. Ensure you have access and the URL is correct."
            }

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        print(
            f"--- Fetching GSC Data for: {actual_site_url} ({start_date} to {end_date}) ---"
        )

        try:
            request = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"],  # Breakdown by keyword
                "rowLimit": 20,  # Top 20 keywords
                "aggregationType": "auto",
            }

            response = (
                self.service.searchanalytics()
                .query(siteUrl=actual_site_url, body=request)
                .execute()
            )

            rows = response.get("rows", [])
            results = []

            for row in rows:
                results.append(
                    {
                        "keyword": row["keys"][0],
                        "clicks": row["clicks"],
                        "impressions": row["impressions"],
                        "ctr": round(row["ctr"] * 100, 2),
                        "position": round(row["position"], 1),
                    }
                )

            return results

        except Exception as e:
            print(f"Error fetching GSC data: {e}")
            return {"error": str(e)}

    def list_sites(self):
        """Lists all sites accessible by the user."""
        try:
            site_list = self.service.sites().list().execute()
            return [s["siteUrl"] for s in site_list.get("siteEntry", [])]
        except Exception as e:
            return []


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    gsc = SearchConsoleService()

    # List sites first to see what we have access to
    sites = gsc.list_sites()
    print("Available Sites:", sites)

    if sites:
        # Test with the first site
        print(gsc.get_organic_performance(sites[0]))
