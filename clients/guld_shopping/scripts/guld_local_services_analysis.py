#!/usr/bin/env python3
"""
Guld Design - Local Services Keyword Analysis
Creates a comprehensive 3-tab deliverable for ear piercing and goldsmith services.
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from backend.services.keyword_planner import KeywordPlannerService

# Configuration
CUSTOMER_ID = "1600121107"
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
)

# Geo Target Constants
GEO_LOCAL_CITIES = [
    "geoTargetConstants/1005182",  # Aabenraa
    "geoTargetConstants/1005192",  # Haderslev
    "geoTargetConstants/1005175",  # Sønderborg
    "geoTargetConstants/1005205",  # Tønder
]
GEO_REGION_SYDDANMARK = ["geoTargetConstants/20252"]
LANGUAGE_DANISH = "1009"

# Landing Pages
LP_EAR_PIERCING = "https://gulddesign.dk/pages/huller-i-orerne"
LP_GOLDSMITH = "https://gulddesign.dk/pages/vaerkstedet"


def run_keyword_research():
    """Run comprehensive keyword research for both service verticals."""
    kp = KeywordPlannerService()
    all_results = {}

    # ========================================
    # PHASE 1: EAR PIERCING (LOCAL)
    # ========================================
    print("=" * 80)
    print("PHASE 1: EAR PIERCING KEYWORDS (LOCAL - 4 Sønderjylland cities)")
    print("=" * 80)

    ear_piercing_seeds = [
        # Core terms
        "huller i ørerne",
        "hul i øret",
        "huller i ørerne pris",
        "huller i ørerne børn",
        "ørehuller",
        "få taget huller i ørerne",
        "ørehul",
        "ørehul pris",
        # Children-specific
        "huller i ørerne børn",
        "børn huller i ørerne",
        "hul i øret barn",
        # Location modifiers
        "huller i ørerne aabenraa",
        "huller i ørerne haderslev",
        "huller i ørerne sønderborg",
        # Service-related
        "ørestikker",
        "første øreringe",
    ]

    print(f"\n[1/2] Querying ear piercing keywords for LOCAL area...")
    try:
        ear_results = kp.generate_keyword_ideas(
            keywords=ear_piercing_seeds,
            location_ids=GEO_LOCAL_CITIES,
            language_id=LANGUAGE_DANISH,
            customer_id=CUSTOMER_ID,
        )
        all_results["ear_piercing_local"] = ear_results
        print(f"    Found {len(ear_results)} keyword ideas")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["ear_piercing_local"] = []

    # ========================================
    # PHASE 2: GOLDSMITH/REPAIRS (REGIONAL)
    # ========================================
    print("\n" + "=" * 80)
    print("PHASE 2: GOLDSMITH/REPAIRS KEYWORDS (REGIONAL - Region Syddanmark)")
    print("=" * 80)

    # 2a. Goldsmith / General
    goldsmith_seeds = [
        "guldsmed",
        "guldsmed aabenraa",
        "guldsmed sønderjylland",
        "guldsmed haderslev",
        "guldsmed sønderborg",
        "guldsmed tønder",
        "smykkebutik",
        "smykkeforretning",
    ]

    print(f"\n[2a] Querying goldsmith keywords...")
    try:
        goldsmith_results = kp.generate_keyword_ideas(
            keywords=goldsmith_seeds,
            location_ids=GEO_REGION_SYDDANMARK,
            language_id=LANGUAGE_DANISH,
            customer_id=CUSTOMER_ID,
        )
        all_results["goldsmith_regional"] = goldsmith_results
        print(f"    Found {len(goldsmith_results)} keyword ideas")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["goldsmith_regional"] = []

    # 2b. Repairs
    repair_seeds = [
        "smykke reparation",
        "ring reparation",
        "kæde reparation",
        "armbånd reparation",
        "halskæde reparation",
        "ring tilpasning",
        "ring størrelsesændring",
        "guld reparation",
        "sølv reparation",
        "reparation af smykker",
        "lodning smykker",
        "kædelodning",
    ]

    print(f"\n[2b] Querying repair keywords...")
    try:
        repair_results = kp.generate_keyword_ideas(
            keywords=repair_seeds,
            location_ids=GEO_REGION_SYDDANMARK,
            language_id=LANGUAGE_DANISH,
            customer_id=CUSTOMER_ID,
        )
        all_results["repairs_regional"] = repair_results
        print(f"    Found {len(repair_results)} keyword ideas")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["repairs_regional"] = []

    # 2c. Custom / Specialty Services
    custom_seeds = [
        "omsmelting guld",
        "smelte guld",
        "gammelt guld til nyt smykke",
        "arvestykke omarbejde",
        "unik ring",
        "specialfremstillet smykke",
        "håndlavet smykke",
        "custom smykke",
        "personlig ring",
        "vielsesring tilpasset",
        "håndlavet vielsesring",
    ]

    print(f"\n[2c] Querying custom/specialty keywords...")
    try:
        custom_results = kp.generate_keyword_ideas(
            keywords=custom_seeds,
            location_ids=GEO_REGION_SYDDANMARK,
            language_id=LANGUAGE_DANISH,
            customer_id=CUSTOMER_ID,
        )
        all_results["custom_regional"] = custom_results
        print(f"    Found {len(custom_results)} keyword ideas")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["custom_regional"] = []

    # 2d. Engraving
    engraving_seeds = [
        "gravering smykker",
        "indgravering ring",
        "indgravering smykker",
        "gravering ring",
        "halskæde med indgravering",
        "armbånd med indgravering",
        "personlig indgravering",
    ]

    print(f"\n[2d] Querying engraving keywords...")
    try:
        engraving_results = kp.generate_keyword_ideas(
            keywords=engraving_seeds,
            location_ids=GEO_REGION_SYDDANMARK,
            language_id=LANGUAGE_DANISH,
            customer_id=CUSTOMER_ID,
        )
        all_results["engraving_regional"] = engraving_results
        print(f"    Found {len(engraving_results)} keyword ideas")
    except Exception as e:
        print(f"    Error: {e}")
        all_results["engraving_regional"] = []

    return all_results


def categorize_keyword(keyword_text):
    """Assign category based on keyword content."""
    text = keyword_text.lower()

    # Ear piercing
    if any(
        term in text
        for term in ["huller", "hul i øre", "ørehul", "piercing øre", "ørestik"]
    ):
        if "børn" in text or "barn" in text:
            return "Ear Piercing - Children"
        return "Ear Piercing"

    # Goldsmith / Local
    if "guldsmed" in text:
        if any(
            city in text
            for city in [
                "aabenraa",
                "åbenrå",
                "haderslev",
                "sønderborg",
                "tønder",
                "sønderjylland",
            ]
        ):
            return "Goldsmith - Local"
        return "Goldsmith"

    # Repairs
    if any(
        term in text
        for term in ["reparation", "tilpasning", "størrelsesændring", "lodning"]
    ):
        return "Repair"

    # Custom / Specialty
    if any(
        term in text
        for term in [
            "omsmelting",
            "smelte",
            "arvestykke",
            "unik",
            "special",
            "håndlavet",
            "custom",
            "personlig",
        ]
    ):
        return "Custom"

    # Engraving
    if any(term in text for term in ["gravering", "indgravering"]):
        return "Engraving"

    # Generic jewelry (lower priority)
    if any(
        term in text
        for term in ["smykke", "ring", "kæde", "armbånd", "halskæde", "øreringe"]
    ):
        return "Generic Jewelry"

    return "Other"


def determine_intent(keyword_text, competition):
    """Determine search intent based on keyword and competition."""
    text = keyword_text.lower()

    # High intent indicators
    high_intent = [
        "pris",
        "køb",
        "book",
        "bestil",
        "nær mig",
        "aabenraa",
        "haderslev",
        "sønderborg",
        "tønder",
    ]
    if any(term in text for term in high_intent):
        return "High"

    # Medium intent (service-seeking)
    medium_intent = [
        "reparation",
        "tilpasning",
        "gravering",
        "huller i ørerne",
        "guldsmed",
    ]
    if any(term in text for term in medium_intent):
        return "High" if competition in ["LOW", "MEDIUM"] else "Medium"

    # Generic terms
    return "Medium"


def should_include(keyword_data, category):
    """Determine if keyword should be included in campaign."""
    text = keyword_data.get("text", "").lower()
    vol = keyword_data.get("avg_monthly_searches", 0)
    comp = keyword_data.get("competition", "")

    # Exclude irrelevant terms
    exclude_terms = [
        "gratis",
        "billig",
        "selv",
        "diy",
        "job",
        "karriere",
        "tattoo",
        "næse",
        "navle",
        "tunge",  # Other piercings
        "køb",
        "online",
        "webshop",  # E-commerce (she's service)
        "kursus",
        "uddannelse",  # Education
        "migræne",  # Medical claims
    ]
    if any(term in text for term in exclude_terms):
        return False

    # Include if it's a core category with any volume
    core_categories = [
        "Ear Piercing",
        "Ear Piercing - Children",
        "Goldsmith - Local",
        "Goldsmith",
        "Repair",
        "Engraving",
        "Custom",
    ]
    if category in core_categories and vol > 0:
        return True

    # Include generic jewelry only if high volume and relevant
    if category == "Generic Jewelry" and vol >= 50:
        return True

    return vol > 0


def process_keywords(raw_results):
    """Process raw keyword data into schema-compliant format."""
    processed = []
    seen = set()

    for category_key, keywords in raw_results.items():
        for kw in keywords:
            text = kw.get("text", "")
            if text in seen:
                continue
            seen.add(text)

            category = categorize_keyword(text)
            competition = kw.get("competition", "Unspecified")
            intent = determine_intent(text, competition)
            include = should_include(kw, category)

            processed.append(
                {
                    "Keyword": text,
                    "Avg. Monthly Searches": kw.get("avg_monthly_searches", 0),
                    "YoY Change": None,  # Not available from API
                    "Competition": (
                        competition.capitalize() if competition else "Unspecified"
                    ),
                    "Top of page bid (low range)": f"DKK {kw.get('low_top_of_page_bid', 0):.2f}",
                    "Top of page bid (high range)": f"DKK {kw.get('high_top_of_page_bid', 0):.2f}",
                    "Category": category,
                    "Intent": intent,
                    "Include": include,
                }
            )

    # Sort by volume descending
    processed.sort(key=lambda x: x["Avg. Monthly Searches"], reverse=True)
    return processed


def build_campaign_structure(keyword_analysis):
    """Build campaign structure from keyword analysis."""
    structure = []

    for kw in keyword_analysis:
        if not kw["Include"]:
            continue

        category = kw["Category"]
        keyword_text = kw["Keyword"]

        # Determine campaign and ad group
        if category in ["Ear Piercing", "Ear Piercing - Children"]:
            campaign = "mb | DA | Search | Huller i Ørerne"
            if "børn" in keyword_text.lower() or "barn" in keyword_text.lower():
                ad_group = "Huller i Ørerne | Børn"
            else:
                ad_group = "Huller i Ørerne | Generelt"
            final_url = LP_EAR_PIERCING
        elif category == "Goldsmith - Local":
            campaign = "mb | DA | Search | Guldsmed Sønderjylland"
            ad_group = "Guldsmed | Sønderjylland"
            final_url = LP_GOLDSMITH
        elif category == "Goldsmith":
            campaign = "mb | DA | Search | Guldsmed Sønderjylland"
            ad_group = "Guldsmed | Generelt"
            final_url = LP_GOLDSMITH
        elif category == "Repair":
            campaign = "mb | DA | Search | Guldsmed Sønderjylland"
            ad_group = "Smykke Reparation"
            final_url = LP_GOLDSMITH
        elif category == "Custom":
            campaign = "mb | DA | Search | Guldsmed Sønderjylland"
            ad_group = "Custom Smykker"
            final_url = LP_GOLDSMITH
        elif category == "Engraving":
            campaign = "mb | DA | Search | Guldsmed Sønderjylland"
            ad_group = "Gravering"
            final_url = LP_GOLDSMITH
        else:
            continue  # Skip generic/other

        # Determine match type
        vol = kw["Avg. Monthly Searches"]
        if vol >= 100 or kw["Intent"] == "High":
            match_type = "Phrase"
        else:
            match_type = "Exact"

        structure.append(
            {
                "Campaign": campaign,
                "Ad Group": ad_group,
                "Keyword": keyword_text,
                "Match Type": match_type,
                "Final URL": final_url,
            }
        )

    return structure


def build_ad_copy(campaign_structure):
    """Build RSA ad copy for each unique ad group."""
    ad_groups = {}
    for row in campaign_structure:
        key = (row["Campaign"], row["Ad Group"])
        if key not in ad_groups:
            ad_groups[key] = row["Final URL"]

    ads = []

    for (campaign, ad_group), final_url in ad_groups.items():
        ad = {
            "Campaign": campaign,
            "Ad Group": ad_group,
            "Final URL": final_url,
        }

        # Generate headlines and descriptions based on ad group
        if "Huller i Ørerne" in ad_group:
            if "Børn" in ad_group:
                ad.update(
                    {
                        "Headline 1": "{KeyWord:Huller i ørerne børn}",
                        "Headline 1 position": 1,
                        "Headline 2": "Professionelt hos guldsmed",
                        "Headline 2 position": "",
                        "Headline 3": "Sterile materialer",
                        "Headline 3 position": "",
                        "Headline 4": "Fra kun 225 kr",
                        "Headline 4 position": "",
                        "Headline 5": "Trygt og smertefrit",
                        "Headline 5 position": "",
                        "Headline 6": "Hypoallergene ørestikker",
                        "Headline 6 position": "",
                        "Headline 7": "Book tid i Aabenraa",
                        "Headline 7 position": "",
                        "Headline 8": "Erfaren guldsmed",
                        "Headline 8 position": "",
                        "Description 1": "Professionel ørepiercing til børn fra 6 år. Sterile materialer og hypoallergene ørestikker. Book tid hos Guld Design i Aabenraa.",
                        "Description 1 position": "",
                        "Description 2": "Tryg atmosfære for dit barn. Vi bruger kun forseglede, sterile pakker. Enkelt hul 225 kr, dobbelt 325 kr.",
                        "Description 2 position": "",
                        "Description 3": "Erfaren guldsmed med fokus på sikkerhed. Personlig vejledning og efterpleje-instruktioner inkluderet.",
                        "Description 3 position": "",
                        "Description 4": "Guld Design i Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290 eller book online.",
                        "Description 4 position": "",
                        "Path 1": "huller-i-orerne",
                        "Path 2": "boern",
                    }
                )
            else:
                ad.update(
                    {
                        "Headline 1": "{KeyWord:Huller i ørerne}",
                        "Headline 1 position": 1,
                        "Headline 2": "Professionel guldsmed",
                        "Headline 2 position": "",
                        "Headline 3": "Sterile materialer",
                        "Headline 3 position": "",
                        "Headline 4": "Fra kun 225 kr",
                        "Headline 4 position": "",
                        "Headline 5": "Trygt og hygiejnisk",
                        "Headline 5 position": "",
                        "Headline 6": "Hypoallergene ørestikker",
                        "Headline 6 position": "",
                        "Headline 7": "Book tid i Aabenraa",
                        "Headline 7 position": "",
                        "Headline 8": "Personlig service",
                        "Headline 8 position": "",
                        "Description 1": "Få taget huller i ørerne hos professionel guldsmed. 100% sterile materialer og hypoallergene ørestikker. Book tid i Aabenraa.",
                        "Description 1 position": "",
                        "Description 2": "Enkelt hul 225 kr, dobbelt 325 kr. Personlig vejledning til valg af ørestikker og præcis placering.",
                        "Description 2 position": "",
                        "Description 3": "Tryg og behagelig atmosfære. Erfaren guldsmed med fokus på hygiejne og sikkerhed. Efterpleje inkluderet.",
                        "Description 3 position": "",
                        "Description 4": "Guld Design, Storegade 11, Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290.",
                        "Description 4 position": "",
                        "Path 1": "huller-i-orerne",
                        "Path 2": "",
                    }
                )
        elif "Guldsmed" in ad_group:
            ad.update(
                {
                    "Headline 1": "{KeyWord:Guldsmed Aabenraa}",
                    "Headline 1 position": 1,
                    "Headline 2": "Professionelt værksted",
                    "Headline 2 position": "",
                    "Headline 3": "Reparation af smykker",
                    "Headline 3 position": "",
                    "Headline 4": "Custom design",
                    "Headline 4 position": "",
                    "Headline 5": "Personlig service",
                    "Headline 5 position": "",
                    "Headline 6": "Erfaren håndværker",
                    "Headline 6 position": "",
                    "Headline 7": "Book gratis vurdering",
                    "Headline 7 position": "",
                    "Headline 8": "Guld & sølv arbejde",
                    "Headline 8 position": "",
                    "Description 1": "Professionel guldsmed i Aabenraa. Reparation, tilpasning og custom design af smykker. Book en gratis vurdering i dag.",
                    "Description 1 position": "",
                    "Description 2": "Personlig service fra erfaren guldsmed. Vi reparerer, omformer og skaber unikke smykker efter dine ønsker.",
                    "Description 2 position": "",
                    "Description 3": "Giv dine arvesmykker nyt liv. Vi omsmelter guld og sølv til nye, personlige designs. Kom forbi værkstedet.",
                    "Description 3 position": "",
                    "Description 4": "Guld Design, Storegade 11, Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290.",
                    "Description 4 position": "",
                    "Path 1": "guldsmed",
                    "Path 2": "aabenraa",
                }
            )
        elif "Reparation" in ad_group:
            ad.update(
                {
                    "Headline 1": "{KeyWord:Smykke reparation}",
                    "Headline 1 position": 1,
                    "Headline 2": "Professionel guldsmed",
                    "Headline 2 position": "",
                    "Headline 3": "Ring tilpasning",
                    "Headline 3 position": "",
                    "Headline 4": "Kæde lodning",
                    "Headline 4 position": "",
                    "Headline 5": "Hurtig service",
                    "Headline 5 position": "",
                    "Headline 6": "Fair priser",
                    "Headline 6 position": "",
                    "Headline 7": "Gratis vurdering",
                    "Headline 7 position": "",
                    "Headline 8": "Aabenraa værksted",
                    "Headline 8 position": "",
                    "Description 1": "Professionel reparation af smykker hos guldsmed i Aabenraa. Ring tilpasning, kædelodning og mere. Gratis vurdering.",
                    "Description 1 position": "",
                    "Description 2": "Erfaren håndværker reparerer dine smykker med omhu. Fra simple kædelodninger til komplekse omformninger.",
                    "Description 2 position": "",
                    "Description 3": "Få dit smykke som nyt igen. Vi reparerer guld, sølv og andre ædelmetaller. Kom forbi for en vurdering.",
                    "Description 3 position": "",
                    "Description 4": "Guld Design, Storegade 11, Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290.",
                    "Description 4 position": "",
                    "Path 1": "reparation",
                    "Path 2": "smykker",
                }
            )
        elif "Custom" in ad_group:
            ad.update(
                {
                    "Headline 1": "{KeyWord:Unik smykke design}",
                    "Headline 1 position": 1,
                    "Headline 2": "Håndlavet efter ønske",
                    "Headline 2 position": "",
                    "Headline 3": "Professionel guldsmed",
                    "Headline 3 position": "",
                    "Headline 4": "Personligt design",
                    "Headline 4 position": "",
                    "Headline 5": "Omsmelting af guld",
                    "Headline 5 position": "",
                    "Headline 6": "Arvestykker omformet",
                    "Headline 6 position": "",
                    "Headline 7": "Book konsultation",
                    "Headline 7 position": "",
                    "Headline 8": "Aabenraa værksted",
                    "Headline 8 position": "",
                    "Description 1": "Få designet dit drømmesmykke. Professionel guldsmed skaber unikke smykker efter dine ønsker. Book en konsultation.",
                    "Description 1 position": "",
                    "Description 2": "Forvandl dine arvesmykker til noget nyt. Vi omsmelter guld og sølv og skaber personlige designs med historie.",
                    "Description 2 position": "",
                    "Description 3": "Håndlavet smykkedesign fra erfaren guldsmed. Du er med i hele processen fra idé til færdigt smykke.",
                    "Description 3 position": "",
                    "Description 4": "Guld Design, Storegade 11, Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290.",
                    "Description 4 position": "",
                    "Path 1": "custom",
                    "Path 2": "smykker",
                }
            )
        elif "Gravering" in ad_group:
            ad.update(
                {
                    "Headline 1": "{KeyWord:Gravering smykker}",
                    "Headline 1 position": 1,
                    "Headline 2": "Personlig indgravering",
                    "Headline 2 position": "",
                    "Headline 3": "Professionel guldsmed",
                    "Headline 3 position": "",
                    "Headline 4": "Ringe og halskæder",
                    "Headline 4 position": "",
                    "Headline 5": "Navne og datoer",
                    "Headline 5 position": "",
                    "Headline 6": "Hurtig levering",
                    "Headline 6 position": "",
                    "Headline 7": "Se eksempler",
                    "Headline 7 position": "",
                    "Headline 8": "Aabenraa værksted",
                    "Headline 8 position": "",
                    "Description 1": "Professionel gravering af smykker. Indgravér navne, datoer eller budskaber i ringe, halskæder og armbånd.",
                    "Description 1 position": "",
                    "Description 2": "Personliggør dit smykke med indgravering. Erfaren guldsmed leverer præcist og smukt håndværk.",
                    "Description 2 position": "",
                    "Description 3": "Giv dit smykke en personlig touch. Vi graverer i guld, sølv og andre materialer. Kom forbi værkstedet.",
                    "Description 3 position": "",
                    "Description 4": "Guld Design, Storegade 11, Aabenraa. Åben man-fre 10-17:30, lør 10-14. Ring 74625290.",
                    "Description 4 position": "",
                    "Path 1": "gravering",
                    "Path 2": "",
                }
            )
        else:
            continue

        ads.append(ad)

    return ads


def main():
    print("=" * 80)
    print("GULD DESIGN - LOCAL SERVICES KEYWORD ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    # Step 1: Run keyword research
    print("\n[STEP 1] Running comprehensive keyword research...")
    raw_results = run_keyword_research()

    # Step 2: Process keywords into Tab 1 format
    print("\n[STEP 2] Processing keywords into schema format...")
    keyword_analysis = process_keywords(raw_results)
    included_count = sum(1 for k in keyword_analysis if k["Include"])
    print(f"    Total keywords: {len(keyword_analysis)}")
    print(f"    Included: {included_count}")

    # Step 3: Build campaign structure (Tab 2)
    print("\n[STEP 3] Building campaign structure...")
    campaign_structure = build_campaign_structure(keyword_analysis)
    print(f"    Total keyword entries: {len(campaign_structure)}")

    # Count by campaign
    campaigns = {}
    for row in campaign_structure:
        campaigns[row["Campaign"]] = campaigns.get(row["Campaign"], 0) + 1
    for camp, count in campaigns.items():
        print(f"    - {camp}: {count} keywords")

    # Step 4: Build ad copy (Tab 3)
    print("\n[STEP 4] Building ad copy...")
    ad_copy = build_ad_copy(campaign_structure)
    print(f"    Total ad groups: {len(ad_copy)}")

    # Step 5: Save outputs
    print("\n[STEP 5] Saving outputs...")

    # Save raw data
    raw_output = os.path.join(OUTPUT_DIR, "guld_local_keywords_raw.json")
    with open(raw_output, "w", encoding="utf-8") as f:
        json.dump(raw_results, f, indent=2, ensure_ascii=False)
    print(f"    Raw data: {raw_output}")

    # Save Tab 1: Keyword Analysis
    tab1_output = os.path.join(OUTPUT_DIR, "guld_tab1_keyword_analysis.json")
    with open(tab1_output, "w", encoding="utf-8") as f:
        json.dump(keyword_analysis, f, indent=2, ensure_ascii=False)
    print(f"    Tab 1 (Keyword Analysis): {tab1_output}")

    # Save Tab 2: Campaign Structure
    tab2_output = os.path.join(OUTPUT_DIR, "guld_tab2_campaign_structure.json")
    with open(tab2_output, "w", encoding="utf-8") as f:
        json.dump(campaign_structure, f, indent=2, ensure_ascii=False)
    print(f"    Tab 2 (Campaign Structure): {tab2_output}")

    # Save Tab 3: Ad Copy
    tab3_output = os.path.join(OUTPUT_DIR, "guld_tab3_ad_copy.json")
    with open(tab3_output, "w", encoding="utf-8") as f:
        json.dump(ad_copy, f, indent=2, ensure_ascii=False)
    print(f"    Tab 3 (Ad Copy): {tab3_output}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\n## TAB 1: KEYWORD ANALYSIS (Top 20)")
    print("-" * 70)
    for kw in keyword_analysis[:20]:
        if kw["Include"]:
            print(f"  ✓ \"{kw['Keyword']}\"")
            print(
                f"      Vol: {kw['Avg. Monthly Searches']} | {kw['Competition']} | {kw['Category']} | Intent: {kw['Intent']}"
            )

    print("\n## TAB 2: CAMPAIGN STRUCTURE")
    print("-" * 70)
    ad_groups = {}
    for row in campaign_structure:
        key = (row["Campaign"], row["Ad Group"])
        ad_groups[key] = ad_groups.get(key, 0) + 1
    for (camp, ag), count in ad_groups.items():
        print(f"  {camp}")
        print(f"    └─ {ag}: {count} keywords")

    print("\n## TAB 3: AD COPY")
    print("-" * 70)
    for ad in ad_copy:
        print(f"  {ad['Campaign']} > {ad['Ad Group']}")
        print(f"    H1: {ad['Headline 1']}")
        print(f"    URL: {ad['Final URL']}")

    print("\n" + "=" * 80)
    print("DONE! Files saved to /output/")
    print("=" * 80)


if __name__ == "__main__":
    main()
