#!/usr/bin/env python3
"""
Guld Design Shopping Campaign Analysis
Pulls fresh data from Google Ads API to analyze Shopping performance
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


def find_guld_design_account(client):
    """Find the Guld Design customer ID."""
    ga_service = client.get_service("GoogleAdsService")
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

    query = """
        SELECT
            customer_client.descriptive_name,
            customer_client.id
        FROM customer_client
        WHERE customer_client.level <= 1
    """

    print("Searching for Guld Design account...")
    try:
        response = ga_service.search_stream(customer_id=login_customer_id, query=query)
        for batch in response:
            for row in batch.results:
                name = row.customer_client.descriptive_name
                cid = str(row.customer_client.id)
                print(f"  Found: {name} (ID: {cid})")
                if "guld" in name.lower() or "guild" in name.lower():
                    print(f"  >>> MATCH: {name} - {cid}")
                    return cid
    except GoogleAdsException as ex:
        print(f"Error: {ex}")
    return None


def get_shopping_campaigns(client, customer_id):
    """Get all Shopping campaigns with performance data."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
            AND campaign.advertising_channel_type IN ('SHOPPING', 'PERFORMANCE_MAX')
    """

    campaigns = []
    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                campaigns.append(
                    {
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "channel_type": row.campaign.advertising_channel_type.name,
                        "bidding_strategy": row.campaign.bidding_strategy_type.name,
                        "budget": row.campaign_budget.amount_micros / 1_000_000,
                        "cost": row.metrics.cost_micros / 1_000_000,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "conversions": row.metrics.conversions,
                        "conv_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "avg_cpc": (
                            row.metrics.average_cpc / 1_000_000
                            if row.metrics.average_cpc
                            else 0
                        ),
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error fetching shopping campaigns: {ex}")

    return campaigns


def get_shopping_product_performance(client, customer_id):
    """Get product-level performance from Shopping campaigns."""
    ga_service = client.get_service("GoogleAdsService")

    # Use shopping_performance_view for product-level data
    query = """
        SELECT
            segments.product_item_id,
            segments.product_title,
            segments.product_brand,
            segments.product_type_l1,
            segments.product_type_l2,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc
        FROM shopping_performance_view
        WHERE segments.date DURING LAST_30_DAYS
    """

    products = []
    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                clicks = row.metrics.clicks
                conversions = row.metrics.conversions

                products.append(
                    {
                        "product_id": row.segments.product_item_id,
                        "product_title": row.segments.product_title,
                        "brand": row.segments.product_brand,
                        "product_type_l1": row.segments.product_type_l1,
                        "product_type_l2": row.segments.product_type_l2,
                        "cost": cost,
                        "impressions": row.metrics.impressions,
                        "clicks": clicks,
                        "conversions": conversions,
                        "conv_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "avg_cpc": (
                            row.metrics.average_cpc / 1_000_000
                            if row.metrics.average_cpc
                            else 0
                        ),
                        "cpa": cost / conversions if conversions > 0 else None,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error fetching product performance: {ex}")

    return products


def get_shopping_search_terms(client, customer_id):
    """Get search terms for Shopping campaigns."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            search_term_view.search_term,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
            AND campaign.advertising_channel_type = 'SHOPPING'
    """

    terms = []
    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                conversions = row.metrics.conversions

                terms.append(
                    {
                        "search_term": row.search_term_view.search_term,
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                        "cost": cost,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "conversions": conversions,
                        "conv_value": row.metrics.conversions_value,
                        "cpa": cost / conversions if conversions > 0 else None,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error fetching search terms: {ex}")

    return terms


def get_device_performance(client, customer_id):
    """Get device performance for Shopping campaigns."""
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            segments.device,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
            AND campaign.advertising_channel_type = 'SHOPPING'
    """

    devices = []
    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in response:
            for row in batch.results:
                cost = row.metrics.cost_micros / 1_000_000
                conversions = row.metrics.conversions

                devices.append(
                    {
                        "campaign_name": row.campaign.name,
                        "device": row.segments.device.name,
                        "cost": cost,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "conversions": conversions,
                        "conv_value": row.metrics.conversions_value,
                        "cpa": cost / conversions if conversions > 0 else None,
                    }
                )
    except GoogleAdsException as ex:
        print(f"Error fetching device data: {ex}")

    return devices


def analyze_and_report(data):
    """Analyze the data and print a report."""
    print("\n" + "=" * 80)
    print("GULD DESIGN SHOPPING CAMPAIGN ANALYSIS")
    print("=" * 80)

    # Campaign Summary
    print("\n## CAMPAIGN OVERVIEW (Last 30 Days)")
    print("-" * 60)
    total_cost = 0
    total_conversions = 0
    for c in data["campaigns"]:
        total_cost += c["cost"]
        total_conversions += c["conversions"]
        cpa = c["cost"] / c["conversions"] if c["conversions"] > 0 else 0
        roas = c["conv_value"] / c["cost"] if c["cost"] > 0 else 0
        print(f"  {c['campaign_name']}")
        print(f"    Status: {c['status']}, Bidding: {c['bidding_strategy']}")
        print(f"    Budget: {c['budget']:.0f} DKK/day")
        print(
            f"    Spend: {c['cost']:.2f} DKK | Clicks: {c['clicks']} | Conv: {c['conversions']:.1f}"
        )
        print(f"    CPA: {cpa:.2f} DKK | ROAS: {roas:.2f}x")
        print()

    print(f"  TOTAL: {total_cost:.2f} DKK spend, {total_conversions:.1f} conversions")
    if total_conversions > 0:
        print(f"  Overall CPA: {total_cost/total_conversions:.2f} DKK")

    # Top Spending Products with 0 Conversions
    print("\n## TOP SPENDING PRODUCTS WITH 0 CONVERSIONS")
    print("-" * 60)
    zero_conv_products = [
        p for p in data["products"] if p["conversions"] == 0 and p["cost"] > 0
    ]
    zero_conv_products.sort(key=lambda x: x["cost"], reverse=True)

    total_wasted = sum(p["cost"] for p in zero_conv_products)
    print(f"  Total wasted spend on 0-conv products: {total_wasted:.2f} DKK")
    print()

    for i, p in enumerate(zero_conv_products[:15], 1):
        print(f"  {i}. {p['product_title'][:50]}...")
        print(
            f"     Brand: {p['brand']} | Cost: {p['cost']:.2f} DKK | Clicks: {p['clicks']}"
        )
        print()

    # Top Search Terms with 0 Conversions
    print("\n## TOP SEARCH TERMS WITH 0 CONVERSIONS")
    print("-" * 60)
    zero_conv_terms = [
        t for t in data["search_terms"] if t["conversions"] == 0 and t["cost"] > 0
    ]
    zero_conv_terms.sort(key=lambda x: x["cost"], reverse=True)

    total_wasted_terms = sum(t["cost"] for t in zero_conv_terms)
    print(f"  Total wasted spend on 0-conv search terms: {total_wasted_terms:.2f} DKK")
    print()

    for i, t in enumerate(zero_conv_terms[:20], 1):
        print(f"  {i}. \"{t['search_term']}\"")
        print(f"     Cost: {t['cost']:.2f} DKK | Clicks: {t['clicks']}")

    # Device Performance
    print("\n## DEVICE PERFORMANCE")
    print("-" * 60)
    device_summary = {}
    for d in data["devices"]:
        device = d["device"]
        if device not in device_summary:
            device_summary[device] = {
                "cost": 0,
                "clicks": 0,
                "conversions": 0,
                "conv_value": 0,
            }
        device_summary[device]["cost"] += d["cost"]
        device_summary[device]["clicks"] += d["clicks"]
        device_summary[device]["conversions"] += d["conversions"]
        device_summary[device]["conv_value"] += d["conv_value"]

    for device, stats in device_summary.items():
        cpa = stats["cost"] / stats["conversions"] if stats["conversions"] > 0 else 0
        roas = stats["conv_value"] / stats["cost"] if stats["cost"] > 0 else 0
        print(f"  {device}:")
        print(
            f"    Cost: {stats['cost']:.2f} DKK | Clicks: {stats['clicks']} | Conv: {stats['conversions']:.1f}"
        )
        print(f"    CPA: {cpa:.2f} DKK | ROAS: {roas:.2f}x")
        print()

    # Brand Analysis
    print("\n## BRAND PERFORMANCE (Products)")
    print("-" * 60)
    brand_summary = {}
    for p in data["products"]:
        brand = p["brand"] or "Unknown"
        if brand not in brand_summary:
            brand_summary[brand] = {
                "cost": 0,
                "clicks": 0,
                "conversions": 0,
                "conv_value": 0,
                "products": 0,
            }
        brand_summary[brand]["cost"] += p["cost"]
        brand_summary[brand]["clicks"] += p["clicks"]
        brand_summary[brand]["conversions"] += p["conversions"]
        brand_summary[brand]["conv_value"] += p["conv_value"]
        brand_summary[brand]["products"] += 1

    # Sort by cost
    sorted_brands = sorted(
        brand_summary.items(), key=lambda x: x[1]["cost"], reverse=True
    )
    for brand, stats in sorted_brands[:10]:
        cpa = (
            stats["cost"] / stats["conversions"]
            if stats["conversions"] > 0
            else float("inf")
        )
        roas = stats["conv_value"] / stats["cost"] if stats["cost"] > 0 else 0
        print(f"  {brand} ({stats['products']} products):")
        print(
            f"    Cost: {stats['cost']:.2f} DKK | Clicks: {stats['clicks']} | Conv: {stats['conversions']:.1f}"
        )
        print(f"    CPA: {cpa:.2f} DKK | ROAS: {roas:.2f}x")
        print()


def main():
    print("Initializing Google Ads API client...")
    client = get_client()

    # Find Guld Design account
    customer_id = find_guld_design_account(client)
    if not customer_id:
        print("ERROR: Could not find Guld Design account!")
        return

    print(f"\nUsing customer ID: {customer_id}")
    print("\nPulling Shopping campaign data...")

    data = {
        "customer_id": customer_id,
        "timestamp": datetime.now().isoformat(),
        "campaigns": [],
        "products": [],
        "search_terms": [],
        "devices": [],
    }

    # Pull all data
    print("  - Fetching Shopping campaigns...")
    data["campaigns"] = get_shopping_campaigns(client, customer_id)
    print(f"    Found {len(data['campaigns'])} Shopping/PMax campaigns")

    print("  - Fetching product performance...")
    data["products"] = get_shopping_product_performance(client, customer_id)
    print(f"    Found {len(data['products'])} products")

    print("  - Fetching search terms...")
    data["search_terms"] = get_shopping_search_terms(client, customer_id)
    print(f"    Found {len(data['search_terms'])} search terms")

    print("  - Fetching device data...")
    data["devices"] = get_device_performance(client, customer_id)
    print(f"    Found {len(data['devices'])} device entries")

    # Save raw data
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output",
        f"guld_shopping_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    )
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw data saved to: {output_path}")

    # Analyze and report
    analyze_and_report(data)

    return data


if __name__ == "__main__":
    main()
