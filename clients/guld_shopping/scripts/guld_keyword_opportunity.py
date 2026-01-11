#!/usr/bin/env python3
"""
Keyword opportunity analysis for Guld Design
Check what's available in the Danish jewelry market
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from backend.services.keyword_planner import KeywordPlannerService


def main():
    print("=" * 80)
    print("GULD DESIGN - KEYWORD OPPORTUNITY ANALYSIS")
    print("=" * 80)

    kp = KeywordPlannerService()
    customer_id = "1600121107"  # Guld Design

    # The brands she carries
    brands = [
        "scrouples smykker",
        "julie sandlau",
        "enamel smykker",
        "studio z smykker",
        "nordahl andersen",
        "susanne friis bjørner",
    ]

    # Generic jewelry terms
    generic_terms = [
        "smykker online",
        "køb smykker",
        "guld smykker",
        "sølv smykker",
        "øreringe guld",
        "halskæde guld",
        "armbånd dame",
        "forlovelsesringe",
    ]

    # Local terms (she's in Aabenraa)
    local_terms = [
        "guldsmed aabenraa",
        "smykker aabenraa",
        "guldsmed sønderjylland",
        "smykkebutik aabenraa",
    ]

    all_results = {}

    # 1. Brand searches
    print("\n[1/3] Checking brand keyword volumes...")
    try:
        brand_results = kp.generate_keyword_ideas(
            keywords=brands,
            location_ids=["geoTargetConstants/2208"],  # Denmark
            language_id="1009",  # Danish
            customer_id=customer_id,
        )
        all_results["brands"] = brand_results
        print(f"    Found {len(brand_results)} brand-related keywords")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["brands"] = []

    # 2. Generic jewelry searches
    print("\n[2/3] Checking generic jewelry keywords...")
    try:
        generic_results = kp.generate_keyword_ideas(
            keywords=generic_terms,
            location_ids=["geoTargetConstants/2208"],
            language_id="1009",
            customer_id=customer_id,
        )
        all_results["generic"] = generic_results
        print(f"    Found {len(generic_results)} generic keywords")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["generic"] = []

    # 3. Local searches
    print("\n[3/3] Checking local Aabenraa keywords...")
    try:
        local_results = kp.generate_keyword_ideas(
            keywords=local_terms,
            location_ids=["geoTargetConstants/2208"],
            language_id="1009",
            customer_id=customer_id,
        )
        all_results["local"] = local_results
        print(f"    Found {len(local_results)} local keywords")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["local"] = []

    # Analysis
    print("\n" + "=" * 80)
    print("KEYWORD ANALYSIS")
    print("=" * 80)

    # Brand keywords
    print("\n## BRAND KEYWORDS (she carries these brands)")
    print("-" * 70)
    if all_results.get("brands"):
        # Sort by volume
        sorted_brands = sorted(
            all_results["brands"],
            key=lambda x: x.get("avg_monthly_searches", 0),
            reverse=True,
        )
        for kw in sorted_brands[:20]:
            vol = kw.get("avg_monthly_searches", 0)
            comp = kw.get("competition", "N/A")
            low_bid = kw.get("low_top_of_page_bid", 0)
            high_bid = kw.get("high_top_of_page_bid", 0)
            print(f"  \"{kw['text']}\"")
            print(
                f"      Vol: {vol:,} | Comp: {comp} | CPC: {low_bid:.2f}-{high_bid:.2f} DKK"
            )
    else:
        print("  No brand keyword data")

    # Generic keywords
    print("\n## GENERIC JEWELRY KEYWORDS (very competitive)")
    print("-" * 70)
    if all_results.get("generic"):
        sorted_generic = sorted(
            all_results["generic"],
            key=lambda x: x.get("avg_monthly_searches", 0),
            reverse=True,
        )
        for kw in sorted_generic[:20]:
            vol = kw.get("avg_monthly_searches", 0)
            comp = kw.get("competition", "N/A")
            low_bid = kw.get("low_top_of_page_bid", 0)
            high_bid = kw.get("high_top_of_page_bid", 0)
            print(f"  \"{kw['text']}\"")
            print(
                f"      Vol: {vol:,} | Comp: {comp} | CPC: {low_bid:.2f}-{high_bid:.2f} DKK"
            )
    else:
        print("  No generic keyword data")

    # Local keywords
    print("\n## LOCAL AABENRAA KEYWORDS (her physical location)")
    print("-" * 70)
    if all_results.get("local"):
        sorted_local = sorted(
            all_results["local"],
            key=lambda x: x.get("avg_monthly_searches", 0),
            reverse=True,
        )
        for kw in sorted_local[:15]:
            vol = kw.get("avg_monthly_searches", 0)
            comp = kw.get("competition", "N/A")
            low_bid = kw.get("low_top_of_page_bid", 0)
            high_bid = kw.get("high_top_of_page_bid", 0)
            print(f"  \"{kw['text']}\"")
            print(
                f"      Vol: {vol:,} | Comp: {comp} | CPC: {low_bid:.2f}-{high_bid:.2f} DKK"
            )
    else:
        print("  No local keyword data")

    # Save results
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output",
        "guld_keyword_opportunity.json",
    )
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to: {output_path}")


if __name__ == "__main__":
    main()
