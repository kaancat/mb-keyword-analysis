#!/usr/bin/env python3
"""
GA4 Partner Clicks report (Data API).

Outputs partner_click counts broken down by partner/component/page.
Requires GA4 OAuth env vars (see backend/.env).
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict, Any

from services.ga4_service import GA4Service
from google.analytics.data_v1beta.types import FilterExpression, Filter


def build_event_filter(event_name: str) -> FilterExpression:
    return FilterExpression(
        filter=Filter(
            field_name="eventName",
            string_filter=Filter.StringFilter(value=event_name),
        )
    )


def run_report(
    svc: GA4Service,
    property_id: str,
    dims: List[str],
    metrics: List[str],
    start_date: str,
    end_date: str,
    limit: int,
    event_name: str,
) -> List[Dict[str, Any]]:
    return svc.run_report(
        property_id=property_id,
        dimensions=dims,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        dimension_filter=build_event_filter(event_name),
        limit=limit,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="GA4 partner_click breakdown report")
    parser.add_argument("--property-id", default="501037449", help="GA4 property ID")
    parser.add_argument("--days", type=int, default=30, help="Number of days back")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (overrides --days)")
    parser.add_argument("--end-date", default="today", help="YYYY-MM-DD or 'today'")
    parser.add_argument("--limit", type=int, default=10000, help="Max rows to return")
    parser.add_argument("--out", default=None, help="Output CSV path (default: stdout)")
    parser.add_argument("--by-date", action="store_true", help="Include date dimension")
    args = parser.parse_args()

    svc = GA4Service()
    if not svc.client:
        print("GA4Service failed to initialize (check OAuth env vars).", file=sys.stderr)
        return 1

    start_date = args.start_date or f"{args.days}daysAgo"
    end_date = args.end_date

    base_dims = [
        "eventName",
        "customEvent:partner_name",
        "customEvent:component",
        "customEvent:page",
    ]
    alt_dims = [
        "eventName",
        "partner_name",
        "component",
        "page",
    ]
    if args.by_date:
        base_dims = ["date"] + base_dims
        alt_dims = ["date"] + alt_dims

    metrics = ["eventCount"]

    data = run_report(
        svc,
        args.property_id,
        base_dims,
        metrics,
        start_date,
        end_date,
        args.limit,
        "partner_click",
    )

    if data and isinstance(data, list) and "error" in data[0]:
        # Retry with alternate dimension names (if customEvent:* is not supported)
        data = run_report(
            svc,
            args.property_id,
            alt_dims,
            metrics,
            start_date,
            end_date,
            args.limit,
            "partner_click",
        )

    if data and isinstance(data, list) and "error" in data[0]:
        print("GA4 report error:", data[0], file=sys.stderr)
        return 1

    # Normalize rows
    rows = []
    for row in data:
        dims = row.get("dimensions", {})
        mets = row.get("metrics", {})
        rows.append({**dims, **mets})

    # Output CSV
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = base_dims + metrics

    out_fh = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    if args.out:
        out_fh.close()
        print(f"Wrote {len(rows)} rows to {args.out}")
    else:
        print(f"\nRows: {len(rows)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
