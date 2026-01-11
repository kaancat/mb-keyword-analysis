#!/usr/bin/env python3
"""
Generate an interactive HTML presentation from keyword analysis artifacts.

Usage:
    python generate_presentation.py <client_directory> [--output <output_path>]

Example:
    python generate_presentation.py clients/mondaybrew
    python generate_presentation.py clients/aeflyt --output deliverables/aeflyt_presentation.html

Required files in client_directory:
    - keyword_analysis.json
    - campaign_structure.json
    - ad_copy.json
    - roi_calculator.json
    - website_content.md (optional, for metadata)
    - potential_analysis.md (optional, for executive summary)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Union, List, Dict


def find_template() -> Path:
    """Find the presentation template file."""
    # Check relative to this script
    script_dir = Path(__file__).parent.parent
    template_path = script_dir / "templates" / "presentation_template.html"

    if template_path.exists():
        return template_path

    # Check common locations
    for path in [
        Path.home()
        / ".claude/plugins/mb-marketplace/plugins/mb-keyword-analysis/templates/presentation_template.html",
        Path("templates/presentation_template.html"),
        Path("presentation_template.html"),
    ]:
        if path.exists():
            return path

    raise FileNotFoundError("Could not find presentation_template.html")


def load_json_file(filepath: Path) -> Union[Dict, List]:
    """Load a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_markdown_metadata(md_path: Path) -> dict:
    """Extract metadata from markdown file."""
    metadata = {}

    if not md_path.exists():
        return metadata

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract client name from heading
    name_match = re.search(
        r"#\s*(?:Website Content|Potentialeanalyse):\s*(.+)", content
    )
    if name_match:
        metadata["client_name"] = name_match.group(1).strip()

    # Extract website URL
    url_match = re.search(r"https?://[^\s\)]+\.(?:dk|no|se|com)", content)
    if url_match:
        metadata["website"] = url_match.group(0)

    # Extract tagline
    tagline_match = re.search(r'"([^"]{10,60})"', content)
    if tagline_match:
        metadata["tagline"] = tagline_match.group(1)

    return metadata


def extract_executive_summary(potential_analysis_path: Path) -> str:
    """Extract executive summary from potential analysis markdown."""
    if not potential_analysis_path.exists():
        return "<p>Denne potentialeanalyse viser hvordan Google Ads kan hjælpe med at få flere kunder.</p>"

    with open(potential_analysis_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find Executive Summary section
    summary_match = re.search(
        r"##\s*1\.\s*Executive Summary\s*\n+([\s\S]*?)(?=\n##|\n---|\Z)", content
    )

    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Convert markdown to HTML
        html = summary_text
        # Convert headers
        html = re.sub(
            r"^###\s*(.+)$",
            r'<h4 class="font-bold text-gray-800 mt-6 mb-2">\1</h4>',
            html,
            flags=re.MULTILINE,
        )
        # Convert bullet points
        html = re.sub(
            r"^\s*-\s+\*\*([^*]+)\*\*:\s*(.+)$",
            r"<li><strong>\1:</strong> \2</li>",
            html,
            flags=re.MULTILINE,
        )
        html = re.sub(r"^\s*-\s+(.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        # Wrap lists
        html = re.sub(
            r"(<li>.*</li>\n?)+",
            r'<ul class="list-disc pl-5 space-y-2 mb-6">\g<0></ul>',
            html,
        )
        # Convert paragraphs
        paragraphs = html.split("\n\n")
        html_parts = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith("<"):
                html_parts.append(f'<p class="mb-4">{p}</p>')
            else:
                html_parts.append(p)
        html = "\n".join(html_parts)
        return html

    return "<p>Denne potentialeanalyse viser hvordan Google Ads kan hjælpe med at få flere kunder.</p>"


def calculate_average_cpc(keywords: list) -> float:
    """Calculate weighted average CPC from keywords."""
    total_weighted = 0
    total_volume = 0

    for kw in keywords:
        volume = kw.get("Avg. Monthly Searches") or kw.get("avg_monthly_searches") or 0
        low_bid = (
            kw.get("Top of page bid (low range)") or kw.get("low_top_of_page_bid") or 0
        )
        high_bid = (
            kw.get("Top of page bid (high range)")
            or kw.get("high_top_of_page_bid")
            or 0
        )

        # Parse bid values
        if isinstance(low_bid, str):
            low_bid = float(re.sub(r"[^\d.]", "", low_bid) or 0)
        if isinstance(high_bid, str):
            high_bid = float(re.sub(r"[^\d.]", "", high_bid) or 0)

        avg_bid = (low_bid + high_bid) / 2
        if volume > 0 and avg_bid > 0:
            total_weighted += avg_bid * volume
            total_volume += volume

    if total_volume > 0:
        return round(total_weighted / total_volume, 2)
    return 25.0  # Default CPC


def generate_presentation(
    client_dir: Path,
    output_path: Optional[Path] = None,
    client_name: Optional[str] = None,
    brand_color: Optional[str] = None,
) -> Path:
    """Generate the HTML presentation from artifacts."""

    # Load required files
    keyword_analysis_path = client_dir / "keyword_analysis.json"
    campaign_structure_path = client_dir / "campaign_structure.json"
    ad_copy_path = client_dir / "ad_copy.json"
    roi_calculator_path = client_dir / "roi_calculator.json"
    website_content_path = client_dir / "website_content.md"
    potential_analysis_path = client_dir / "potential_analysis.md"
    brand_path = client_dir / "brand.json"

    # Load brand assets if available
    brand_data = {}
    if brand_path.exists():
        brand_data = load_json_file(brand_path)
        print(f"Using brand assets from: {brand_path}")

    # Validate required files
    for path in [keyword_analysis_path, campaign_structure_path, ad_copy_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    # Load data
    keywords = load_json_file(keyword_analysis_path)
    campaign_structure = load_json_file(campaign_structure_path)
    ads = load_json_file(ad_copy_path)

    # Handle nested structure (some files have {"keywords": [...]})
    if isinstance(keywords, dict) and "keywords" in keywords:
        keywords = keywords["keywords"]
    if isinstance(campaign_structure, dict) and "structure" in campaign_structure:
        campaign_structure = campaign_structure["structure"]
    if isinstance(ads, dict) and "ads" in ads:
        ads = ads["ads"]

    # Load ROI data
    roi_data = {}
    if roi_calculator_path.exists():
        roi_data = load_json_file(roi_calculator_path)

    # Extract metadata
    metadata = parse_markdown_metadata(website_content_path)

    # Use brand.json values if available, then fallback to metadata, then defaults
    if not client_name:
        client_name = (
            brand_data.get("brand_name")
            or metadata.get("client_name")
            or client_dir.name.replace("_", " ").title()
        )

    website = (
        brand_data.get("url")
        or metadata.get("website")
        or f"https://{client_dir.name}.dk"
    )
    tagline = metadata.get("tagline", "Din partner i vækst")

    # Use brand colors from brand.json if available
    if not brand_color:
        brand_color = brand_data.get("primary_color", "#2b74b8")
    accent_color = brand_data.get("accent_color", "#f5822d")
    logo_url = brand_data.get("logo_url", "")

    # Get ROI values
    budget = roi_data.get("budget", 5000)
    profit_per_customer = roi_data.get("profit_per_customer", 2500)
    close_rate = (
        int(roi_data.get("close_rate", 0.2) * 100)
        if roi_data.get("close_rate", 0) < 1
        else roi_data.get("close_rate", 20)
    )
    cpc = roi_data.get("cpc", calculate_average_cpc(keywords))
    conversion_rate = (
        int(roi_data.get("conversion_rate", 0.05) * 100)
        if roi_data.get("conversion_rate", 0) < 1
        else roi_data.get("conversion_rate", 5)
    )
    currency = roi_data.get("currency", "DKK")

    # Extract executive summary
    executive_summary = extract_executive_summary(potential_analysis_path)

    # Load template
    template_path = find_template()
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Prepare replacements
    replacements = {
        "{{CLIENT_NAME}}": client_name,
        "{{CLIENT_LOGO}}": logo_url,
        "{{CLIENT_TAGLINE}}": tagline,
        "{{CLIENT_WEBSITE}}": website,
        "{{CLIENT_CTA}}": f"{website}/kontakt/" if website else "#",
        "{{SUMMARY_SUBTITLE}}": "Datadrevet plan for at nå flere kunder via Google Ads.",
        "{{EXECUTIVE_SUMMARY}}": executive_summary,
        "{{BRAND_COLOR}}": brand_color,
        "{{BRAND_LIGHT}}": brand_color,
        "{{BRAND_DARK}}": "#0f2f4a",
        "{{ACCENT_COLOR}}": accent_color,
        "{{KEYWORDS_JSON}}": json.dumps(keywords, ensure_ascii=False, indent=4),
        "{{CAMPAIGN_STRUCTURE_JSON}}": json.dumps(
            campaign_structure, ensure_ascii=False, indent=4
        ),
        "{{ADS_JSON}}": json.dumps(ads, ensure_ascii=False, indent=4),
        "{{BUDGET}}": str(budget),
        "{{PROFIT_PER_CUSTOMER}}": str(profit_per_customer),
        "{{CLOSE_RATE}}": str(close_rate),
        "{{CPC}}": str(cpc),
        "{{CONVERSION_RATE}}": str(conversion_rate),
        "{{CURRENCY}}": currency,
    }

    # Apply replacements
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))

    # Determine output path
    if output_path is None:
        output_path = client_dir / "presentation.html"

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Presentation generated: {output_path}")
    print(f"  - Client: {client_name}")
    print(f"  - Keywords: {len(keywords)}")
    print(f"  - Campaign entries: {len(campaign_structure)}")
    print(f"  - Ads: {len(ads)}")
    print(f"  - Budget: {currency} {budget:,}")
    print(f"  - Estimated CPC: {currency} {cpc:.2f}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML presentation from keyword analysis artifacts."
    )
    parser.add_argument(
        "client_dir",
        type=Path,
        help="Path to client directory containing JSON artifacts",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output path for the presentation (default: <client_dir>/presentation.html)",
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default=None,
        help="Client name (default: extracted from artifacts or directory name)",
    )
    parser.add_argument(
        "--color",
        "-c",
        type=str,
        default="#2b74b8",
        help="Brand color in hex format (default: #2b74b8)",
    )

    args = parser.parse_args()

    if not args.client_dir.exists():
        print(f"Error: Directory not found: {args.client_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        output_path = generate_presentation(
            client_dir=args.client_dir,
            output_path=args.output,
            client_name=args.name,
            brand_color=args.color,
        )
        print(f"\nOpen in browser: file://{output_path.absolute()}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
