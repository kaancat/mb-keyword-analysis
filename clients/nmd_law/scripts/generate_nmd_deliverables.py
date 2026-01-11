import json
import csv
import os

def generate_deliverables():
    # Load raw data
    with open("output/nmd_keyword_research_raw.json", "r") as f:
        raw_data = json.load(f)
        
    # Define Ad Groups and their keywords
    ad_groups = {
        "Permanent Ophold | General": {
            "keywords": [],
            "url": "https://www.nmdlawgroup.com/permanent-opholdstilladelse"
        },
        "Familiesammenføring | General": {
            "keywords": [],
            "url": "https://www.nmdlawgroup.com/familiesammenfoering"
        },
        "Opholdstilladelse | General": {
            "keywords": [],
            "url": "https://www.nmdlawgroup.com/udlaendingeret"
        },
        "Advokat | Udlændingeret": {
            "keywords": [
                "advokat udlændingeret",
                "advokat familiesammenføring",
                "advokat permanent opholdstilladelse",
                "advokat opholdstilladelse",
                "udlændinge advokat"
            ],
            "url": "https://www.nmdlawgroup.com/udlaendingeret"
        },
        "English | Expat Services": {
            "keywords": [],
            "url": "https://www.nmdlawgroup.com/udlaendingeret" # Fallback, ideally specific English page
        }
    }
    
    # Process raw data into Ad Groups
    # Permanent Ophold
    for item in raw_data.get("permanent_ophold", []):
        text = item["text"]
        if "permanent" in text and "ophold" in text:
            ad_groups["Permanent Ophold | General"]["keywords"].append(item)
            
    # Familiesammenføring
    for item in raw_data.get("familiesammenfoering", []):
        text = item["text"]
        if "familie" in text or "ægtefælle" in text:
            ad_groups["Familiesammenføring | General"]["keywords"].append(item)
            
    # Opholdstilladelse (General)
    for item in raw_data.get("opholdstilladelse", []):
        text = item["text"]
        if "permanent" in text: continue
        if "familie" in text: continue
        ad_groups["Opholdstilladelse | General"]["keywords"].append(item)
        
    # English Expat
    for item in raw_data.get("english_expat", []):
        ad_groups["English | Expat Services"]["keywords"].append(item)

    # 1. Generate Keywords Tab Data (JSON for Sheet)
    keywords_tab_data = []
    
    for ag_name, data in ad_groups.items():
        for kw_item in data["keywords"]:
            kw_text = kw_item if isinstance(kw_item, str) else kw_item["text"]
            vol = kw_item.get("avg_monthly_searches", 0) if isinstance(kw_item, dict) else 0
            comp = kw_item.get("competition", "Unspecified") if isinstance(kw_item, dict) else "Unspecified"
            
            # Phrase match for most
            keywords_tab_data.append({
                "Campaign": "mb | DA | Search | Udlændingeret",
                "Ad Group": ag_name,
                "Keyword": kw_text,
                "Match Type": "Phrase",
                "Avg. Monthly Searches": vol,
                "Competition": comp,
                "Top of page bid (low range)": "DKK 5.00", # Estimated
                "Top of page bid (high range)": "DKK 15.00", # Estimated
                "Intent": "High" if "advokat" in kw_text or "lawyer" in kw_text else "Medium",
                "Include": True
            })
            
            # Exact match for high intent
            if "advokat" in kw_text or "lawyer" in kw_text or kw_text in ["permanent opholdstilladelse", "familiesammenføring"]:
                keywords_tab_data.append({
                    "Campaign": "mb | DA | Search | Udlændingeret",
                    "Ad Group": ag_name,
                    "Keyword": kw_text,
                    "Match Type": "Exact",
                    "Avg. Monthly Searches": vol,
                    "Competition": comp,
                    "Top of page bid (low range)": "DKK 5.00",
                    "Top of page bid (high range)": "DKK 15.00",
                    "Intent": "High",
                    "Include": True
                })
                
    with open("output/nmd_keywords_tab.json", "w") as f:
        json.dump(keywords_tab_data, f, indent=2, ensure_ascii=False)
        
    # 2. Generate Ads Tab Data
    ads_tab_data = []
    
    # Common assets
    headlines_common = [
        "Specialister i Udlændingeret",
        "Få Hjælp til Din Sag",
        "Erfaren Udlændinge Advokat",
        "NMD Law Group",
        "Gratis Vurdering af Sagen",
        "Vi Kender Reglerne",
        "Personlig Rådgivning",
        "Kontakt Os i Dag"
    ]
    
    descriptions_common = [
        "Vi hjælper med permanent ophold, familiesammenføring og opholdstilladelse. Kontakt os.",
        "Få en gratis vurdering af din sag inden for 48 timer. Erfarne jurister står klar.",
        "Vi har stor erfaring med udlændingeret og sikrer dig den bedste behandling af din sag."
    ]
    
    for ag_name, data in ad_groups.items():
        # Customize headlines based on Ad Group
        headlines = headlines_common.copy()
        descriptions = descriptions_common.copy()
        
        if "English" in ag_name:
            headlines = [
                "Immigration Lawyer Denmark",
                "Residence Permit Help",
                "Family Reunification",
                "Permanent Residence",
                "NMD Law Group",
                "Free Case Assessment",
                "Expert Legal Advice",
                "Contact Us Today"
            ]
            descriptions = [
                "We help with permanent residence, family reunification, and work permits in Denmark.",
                "Get a free assessment of your case within 48 hours. Experienced lawyers ready to help.",
                "Specialized in Danish immigration law. We ensure the best handling of your case."
            ]
        elif "Permanent" in ag_name:
            headlines.insert(0, "Få Permanent Opholdstilladelse")
            headlines.insert(1, "Hjælp til Permanent Ophold")
            headlines.insert(2, "Regler for Permanent Ophold")
        elif "Familie" in ag_name:
            headlines.insert(0, "Hjælp til Familiesammenføring")
            headlines.insert(1, "Få Din Familie til Danmark")
            headlines.insert(2, "Regler for Familiesammenføring")
        elif "Advokat" in ag_name:
            headlines.insert(0, "Brug for en Udlændinge Advokat?")
            headlines.insert(1, "Ekspert i Udlændingeret")
        else:
            headlines.insert(0, "Hjælp til Opholdstilladelse")
            headlines.insert(1, "Søg om Opholdstilladelse")
            
        ad = {
            "Campaign": "mb | DA | Search | Udlændingeret",
            "Ad Group": ag_name,
            "Final URL": data["url"]
        }
        
        # Add Headlines 1-15
        for i, h in enumerate(headlines[:15], 1):
            ad[f"Headline {i}"] = h
            ad[f"Headline {i} position"] = "" # No pinning by default
            
        # Add Descriptions 1-4
        for i, d in enumerate(descriptions[:4], 1):
            ad[f"Description {i}"] = d
            ad[f"Description {i} position"] = ""
            
        ad["Path 1"] = "advokat"
        ad["Path 2"] = "udlaendingeret"
        
        ads_tab_data.append(ad)
        
    with open("output/nmd_ads_tab.json", "w") as f:
        json.dump(ads_tab_data, f, indent=2, ensure_ascii=False)
        
    # 3. Generate Campaign Structure Tab Data
    structure_tab_data = []
    for ag_name, data in ad_groups.items():
        structure_tab_data.append({
            "Campaign": "mb | DA | Search | Udlændingeret",
            "Ad Group": ag_name,
            "Keyword": "", # Structure tab usually lists ad groups, but schema might require keyword mapping. 
                           # For simplicity in this script, we'll list unique Ad Groups.
                           # Actually, the schema often wants a row per keyword or just Ad Group level.
                           # Let's follow the golden example: Campaign, Ad Group, Keyword, Match Type, Final URL.
                           # We will replicate the keyword list here but for the structure tab.
            "Match Type": "",
            "Final URL": data["url"]
        })
        
    # Re-generating structure to match schema (Campaign, Ad Group, Keyword, Match Type, Final URL)
    structure_rows = []
    for item in keywords_tab_data:
        structure_rows.append({
            "Campaign": item["Campaign"],
            "Ad Group": item["Ad Group"],
            "Keyword": item["Keyword"],
            "Match Type": item["Match Type"],
            "Final URL": ad_groups[item["Ad Group"]]["url"]
        })

    with open("output/nmd_campaign_structure_tab.json", "w") as f:
        json.dump(structure_rows, f, indent=2, ensure_ascii=False)

    print("Deliverables generated in output/ (nmd_keywords_tab.json, nmd_ads_tab.json, nmd_campaign_structure_tab.json)")

if __name__ == "__main__":
    generate_deliverables()
