#!/usr/bin/env python3
"""
Deep analysis of Guld Design account:
- Full account performance
- Auction insights (competitors)
- Search terms that DID convert (historically)
- Device/geo breakdown
- What's actually working vs not
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_client():
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip(),
        "use_proto_plus": "True",
    }
    return GoogleAdsClient.load_from_dict(config)


CUSTOMER_ID = "1600121107"


def get_all_campaigns_performance(client, date_range="LAST_30_DAYS"):
    """Get all campaigns performance for the last year."""
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING {date_range}
    """

    campaigns = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                conv = row.metrics.conversions
                campaigns.append(
                    {
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "channel_type": row.campaign.advertising_channel_type.name,
                        "bidding_strategy": row.campaign.bidding_strategy_type.name,
                        "cost": cost,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "conversions": conv,
                        "conv_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "avg_cpc": (
                            row.metrics.average_cpc / 1_000_000
                            if row.metrics.average_cpc
                            else 0
                        ),
                        "cpa": cost / conv if conv > 0 else None,
                        "roas": row.metrics.conversions_value / cost if cost > 0 else 0,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error: {ex}")

    return campaigns


def get_converting_search_terms(client):
    """Get search terms that actually converted - all time."""
    ga_service = client.get_service("GoogleAdsService")

    # Last 30 days for search terms
    query = """
        SELECT
            search_term_view.search_term,
            campaign.name,
            metrics.cost_micros,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
            AND metrics.conversions > 0
        ORDER BY metrics.conversions DESC
        LIMIT 100
    """

    terms = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                conv = row.metrics.conversions
                terms.append(
                    {
                        "search_term": row.search_term_view.search_term,
                        "campaign": row.campaign.name,
                        "cost": cost,
                        "clicks": row.metrics.clicks,
                        "conversions": conv,
                        "conv_value": row.metrics.conversions_value,
                        "cpa": cost / conv if conv > 0 else None,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error getting converting terms: {ex}")

    return terms


def get_auction_insights(client):
    """Get auction insights - who are we competing against."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.name,
            segments.auction_insight_domain,
            metrics.auction_insight_search_impression_share,
            metrics.auction_insight_search_overlap_rate,
            metrics.auction_insight_search_outranking_share
        FROM campaign_auction_insight
        WHERE segments.date DURING LAST_30_DAYS
    """

    insights = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                insights.append(
                    {
                        "campaign": row.campaign.name,
                        "competitor": row.segments.auction_insight_domain,
                        "impression_share": row.metrics.auction_insight_search_impression_share,
                        "overlap_rate": row.metrics.auction_insight_search_overlap_rate,
                        "outranking_share": row.metrics.auction_insight_search_outranking_share,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error getting auction insights: {ex}")

    return insights


def get_geo_performance(client):
    """Geographic performance - where do conversions come from."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            geographic_view.country_criterion_id,
            geographic_view.location_type,
            campaign.name,
            metrics.cost_micros,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM geographic_view
        WHERE segments.date DURING LAST_30_DAYS
            AND metrics.impressions > 0
    """

    geo = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                geo.append(
                    {
                        "country_id": row.geographic_view.country_criterion_id,
                        "location_type": row.geographic_view.location_type.name,
                        "campaign": row.campaign.name,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "clicks": row.metrics.clicks,
                        "conversions": row.metrics.conversions,
                        "conv_value": row.metrics.conversions_value,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error getting geo data: {ex}")

    return geo


def get_device_performance(client):
    """Device breakdown for all campaigns."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.name,
            segments.device,
            metrics.cost_micros,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
    """

    devices = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                devices.append(
                    {
                        "campaign": row.campaign.name,
                        "device": row.segments.device.name,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "clicks": row.metrics.clicks,
                        "conversions": row.metrics.conversions,
                        "conv_value": row.metrics.conversions_value,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error getting device data: {ex}")

    return devices


def get_top_search_terms_by_spend(client):
    """Top search terms by spend - see where money goes."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            search_term_view.search_term,
            campaign.name,
            campaign.advertising_channel_type,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 200
    """

    terms = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                conv = row.metrics.conversions
                terms.append(
                    {
                        "search_term": row.search_term_view.search_term,
                        "campaign": row.campaign.name,
                        "channel": row.campaign.advertising_channel_type.name,
                        "cost": cost,
                        "clicks": row.metrics.clicks,
                        "impressions": row.metrics.impressions,
                        "conversions": conv,
                        "conv_value": row.metrics.conversions_value,
                        "cpa": cost / conv if conv > 0 else None,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error: {ex}")

    return terms


def main():
    print("=" * 80)
    print("GULD DESIGN - DEEP ACCOUNT ANALYSIS")
    print("=" * 80)

    client = get_client()

    data = {}

    # 1. All campaigns - last year
    print("\n[1/6] Fetching all campaigns (last 365 days)...")
    data["campaigns"] = get_all_campaigns_performance(client)
    print(f"    Found {len(data['campaigns'])} campaigns")

    # 2. Converting search terms
    print("\n[2/6] Fetching search terms that converted...")
    data["converting_terms"] = get_converting_search_terms(client)
    print(f"    Found {len(data['converting_terms'])} converting search terms")

    # 3. Auction insights
    print("\n[3/6] Fetching auction insights (competitors)...")
    data["auction_insights"] = get_auction_insights(client)
    print(f"    Found {len(data['auction_insights'])} competitor entries")

    # 4. Geographic performance
    print("\n[4/6] Fetching geographic performance...")
    data["geo"] = get_geo_performance(client)
    print(f"    Found {len(data['geo'])} geo entries")

    # 5. Device performance
    print("\n[5/6] Fetching device performance...")
    data["devices"] = get_device_performance(client)
    print(f"    Found {len(data['devices'])} device entries")

    # 6. Top search terms by spend
    print("\n[6/6] Fetching top search terms by spend (last 90 days)...")
    data["top_terms_by_spend"] = get_top_search_terms_by_spend(client)
    print(f"    Found {len(data['top_terms_by_spend'])} search terms")

    # Save raw data
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output",
        f"guld_deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    )
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nRaw data saved to: {output_path}")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    # Campaign summary
    print("\n## ALL CAMPAIGNS (Last 365 Days)")
    print("-" * 70)
    total_cost = sum(c["cost"] for c in data["campaigns"])
    total_conv = sum(c["conversions"] for c in data["campaigns"])
    total_value = sum(c["conv_value"] for c in data["campaigns"])

    print(f"Total spend: {total_cost:,.2f} DKK")
    print(f"Total conversions: {total_conv:.1f}")
    print(f"Total revenue: {total_value:,.2f} DKK")
    print(f"Overall ROAS: {total_value/total_cost:.2f}x" if total_cost > 0 else "N/A")
    print(f"Overall CPA: {total_cost/total_conv:.2f} DKK" if total_conv > 0 else "N/A")
    print()

    # Sort by conversions
    sorted_campaigns = sorted(
        data["campaigns"], key=lambda x: x["conversions"], reverse=True
    )
    for c in sorted_campaigns[:10]:
        roas = c["roas"]
        cpa = c["cpa"] if c["cpa"] else 0
        print(f"  {c['campaign_name'][:45]:<45} | {c['status']:<8}")
        print(
            f"      Cost: {c['cost']:>8,.0f} | Conv: {c['conversions']:>5.1f} | Value: {c['conv_value']:>10,.0f} | ROAS: {roas:>5.2f}x | CPA: {cpa:>6.0f}"
        )
        print()

    # Converting search terms
    print("\n## SEARCH TERMS THAT CONVERTED (Last 365 Days)")
    print("-" * 70)
    if data["converting_terms"]:
        for t in data["converting_terms"][:20]:
            cpa = t["cpa"] if t["cpa"] else 0
            print(f"  \"{t['search_term'][:40]}\"")
            print(
                f"      Conv: {t['conversions']:.1f} | Value: {t['conv_value']:,.0f} DKK | CPA: {cpa:.0f} DKK"
            )
    else:
        print("  No converting search terms found in last 365 days!")

    # Auction insights - aggregate by competitor
    print("\n## TOP COMPETITORS (Auction Insights)")
    print("-" * 70)
    if data["auction_insights"]:
        competitor_agg = {}
        for i in data["auction_insights"]:
            comp = i["competitor"]
            if comp not in competitor_agg:
                competitor_agg[comp] = {
                    "impression_share": [],
                    "overlap_rate": [],
                    "outranking_share": [],
                }
            competitor_agg[comp]["impression_share"].append(i["impression_share"] or 0)
            competitor_agg[comp]["overlap_rate"].append(i["overlap_rate"] or 0)
            competitor_agg[comp]["outranking_share"].append(i["outranking_share"] or 0)

        # Average and sort by overlap
        competitor_summary = []
        for comp, stats in competitor_agg.items():
            avg_overlap = (
                sum(stats["overlap_rate"]) / len(stats["overlap_rate"])
                if stats["overlap_rate"]
                else 0
            )
            avg_is = (
                sum(stats["impression_share"]) / len(stats["impression_share"])
                if stats["impression_share"]
                else 0
            )
            avg_outrank = (
                sum(stats["outranking_share"]) / len(stats["outranking_share"])
                if stats["outranking_share"]
                else 0
            )
            competitor_summary.append(
                {
                    "competitor": comp,
                    "avg_overlap": avg_overlap,
                    "avg_impression_share": avg_is,
                    "avg_outranking": avg_outrank,
                }
            )

        competitor_summary.sort(key=lambda x: x["avg_overlap"], reverse=True)

        for c in competitor_summary[:15]:
            print(f"  {c['competitor'][:40]:<40}")
            print(
                f"      Overlap: {c['avg_overlap']*100:>5.1f}% | Their IS: {c['avg_impression_share']*100:>5.1f}% | We outrank: {c['avg_outranking']*100:>5.1f}%"
            )
    else:
        print("  No auction insights available")

    # Device summary
    print("\n## DEVICE PERFORMANCE (Last 365 Days)")
    print("-" * 70)
    device_agg = {}
    for d in data["devices"]:
        dev = d["device"]
        if dev not in device_agg:
            device_agg[dev] = {
                "cost": 0,
                "clicks": 0,
                "conversions": 0,
                "conv_value": 0,
            }
        device_agg[dev]["cost"] += d["cost"]
        device_agg[dev]["clicks"] += d["clicks"]
        device_agg[dev]["conversions"] += d["conversions"]
        device_agg[dev]["conv_value"] += d["conv_value"]

    for dev, stats in device_agg.items():
        cpa = stats["cost"] / stats["conversions"] if stats["conversions"] > 0 else 0
        roas = stats["conv_value"] / stats["cost"] if stats["cost"] > 0 else 0
        conv_rate = (
            (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
        )
        print(f"  {dev}:")
        print(f"      Cost: {stats['cost']:,.0f} DKK | Clicks: {stats['clicks']:,}")
        print(
            f"      Conv: {stats['conversions']:.1f} ({conv_rate:.2f}%) | Value: {stats['conv_value']:,.0f} DKK"
        )
        print(f"      CPA: {cpa:.0f} DKK | ROAS: {roas:.2f}x")
        print()

    # Top spend terms with 0 conversions (wasters)
    print("\n## TOP WASTER SEARCH TERMS (90 days, 0 conversions)")
    print("-" * 70)
    wasters = [t for t in data["top_terms_by_spend"] if t["conversions"] == 0]
    total_wasted = sum(t["cost"] for t in wasters)
    print(f"  Total wasted on 0-conv terms: {total_wasted:,.2f} DKK")
    print()
    for t in wasters[:25]:
        print(f"  \"{t['search_term'][:45]}\" ({t['channel']})")
        print(f"      Cost: {t['cost']:.2f} DKK | Clicks: {t['clicks']}")

    return data


if __name__ == "__main__":
    main()
