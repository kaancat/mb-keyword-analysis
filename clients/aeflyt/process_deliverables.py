import json
import os

def main():
    base_dir = os.path.dirname(__file__)
    raw_path = os.path.join(base_dir, 'keyword_data_raw.json')
    
    with open(raw_path, 'r') as f:
        raw_data = json.load(f)
        
    # --- Tab 1: Keyword Analysis ---
    keyword_analysis = []
    for item in raw_data:
        keyword_analysis.append({
            "Keyword": item['text'],
            "Avg. Monthly Searches": item['avg_monthly_searches'],
            "Competition": item['competition'].title(), # Fix case for schema
            "Category": "Moving Services", # Simplified
            "Intent": "High" if "pris" in item['text'] or "tilbud" in item['text'] else "Medium",
            "Include": True
        })
        
    with open(os.path.join(base_dir, 'keyword_analysis.json'), 'w') as f:
        json.dump(keyword_analysis, f, indent=4)
        
    # --- Tab 2: Campaign Structure ---
    campaign_structure = []
    
    # Simple logic to group keywords
    # Campaign: Business vs Private vs General
    
    for item in raw_data:
        kw = item['text'].lower()
        campaign_name = ""
        ad_group = ""
        
        if "erhverv" in kw or "kontor" in kw:
            campaign_name = "mb | DK | Search | Business Moving"
            ad_group = "Business Moving | General"
        elif "privat" in kw or "hus" in kw or "lejlighed" in kw:
            campaign_name = "mb | DK | Search | Private Moving"
            ad_group = "Private Moving | General"
        else:
            campaign_name = "mb | DK | Search | General Moving"
            ad_group = "Moving Company | General"
            
        campaign_structure.append({
            "Campaign": campaign_name,
            "Ad Group": ad_group,
            "Keyword": kw,
            "Match Type": "Phrase",
            "Final URL": "https://aeflyt.dk/"
        })
        
    with open(os.path.join(base_dir, 'campaign_structure.json'), 'w') as f:
        json.dump(campaign_structure, f, indent=4)

    # --- Tab 3: Ad Copy ---
    # Generate one sample ad per unique ad group
    ad_copy = []
    unique_ad_groups = set()
    for item in campaign_structure:
        key = (item['Campaign'], item['Ad Group'])
        if key not in unique_ad_groups:
            unique_ad_groups.add(key)
            
            # Determine headlines based on campaign
            h1 = "{KeyWord:Flyttefirma}"
            h2 = "Flytning med kærlig hånd"
            desc1 = "Vi gør din flytning nem og overskuelig. Få et uforpligtende tilbud i dag."
            
            if "Business" in item['Campaign']:
                h1 = "{KeyWord:Erhvervsflytning}"
                h2 = "Effektiv kontorflytning"
                desc1 = "Minimer nedetid med vores professionelle erhvervsflytning. Vi flytter for din virksomhed."
            
            ad_copy.append({
                "Campaign": item['Campaign'],
                "Ad Group": item['Ad Group'],
                "Headline 1": h1,
                "Headline 1 position": 1,
                "Headline 2": h2,
                "Headline 2 position": 2,
                "Headline 3": "Få et uforpligtende tilbud",
                "Headline 3 position": "",
                "Description 1": desc1,
                "Description 1 position": 1,
                "Description 2": "Sikker transport og opbevaring. Kontakt os for en skræddersyet løsning.",
                "Final URL": "https://aeflyt.dk/"
            })
            
    with open(os.path.join(base_dir, 'ad_copy.json'), 'w') as f:
        json.dump(ad_copy, f, indent=4)

    # --- Tab 4: ROI Calculator ---
    roi_data = {
        "client_inputs": {
            "budget": 5000,
            "profit_per_customer": 2000,
            "close_rate": 20
        },
        "campaign_estimates": {
            "cpc": 15,
            "website_conv_rate": 5
        },
        "calculated_outputs": {
            # These are usually auto-calculated by the sheet/frontend, but we provide estimates here
            "estimated_clicks": 333,
            "estimated_leads": 16.6,
            "estimated_customers": 3.3,
            "estimated_revenue": 6600,
            "estimated_profit": 1600,
            "roas": "1.32x",
            "status": "✅ Profitable"
        }
    }
    
    with open(os.path.join(base_dir, 'roi_calculator.json'), 'w') as f:
        json.dump(roi_data, f, indent=4)
        
    print("Generated all deliverables successfully.")

if __name__ == "__main__":
    main()
