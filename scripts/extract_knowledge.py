import os
import json
import pandas as pd
from docx import Document
import glob

BASE_DIR = "/Users/kaancatalkaya/Desktop/Projects/Google Ads - mondaybrew/knowledge_base/Data Examples"
OUTPUT_FILE = "/Users/kaancatalkaya/Desktop/Projects/Google Ads - mondaybrew/backend/knowledge_base/extracted_raw.json"

def extract_excel_patterns(file_path):
    """Extracts structure and patterns from Excel case studies."""
    try:
        # Read first few rows to get headers and structure
        df = pd.read_excel(file_path, nrows=50) 
        
        # Normalize columns
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        patterns = {
            "file": os.path.basename(file_path),
            "columns": list(df.columns),
            "sample_rows": [],
            "match_type_stats": {},
            "naming_samples": []
        }
        
        # Extract Match Type Stats
        if 'match type' in df.columns:
            patterns['match_type_stats'] = df['match type'].value_counts().to_dict()
            
        # Extract Naming Samples (Campaign, Ad Group)
        if 'campaign' in df.columns:
            patterns['naming_samples'].extend(df['campaign'].dropna().unique()[:5].tolist())
        if 'ad group' in df.columns:
            patterns['naming_samples'].extend(df['ad group'].dropna().unique()[:5].tolist())
            
        # Sample Rows (for RAG examples)
        # Convert top 5 rows to dict, handling datetimes by converting to string
        patterns['sample_rows'] = df.head(5).astype(str).to_dict(orient='records')
        
        return patterns
    except Exception as e:
        return {"file": os.path.basename(file_path), "error": str(e)}

def extract_docx_rules(file_path):
    """Extracts rule-like sentences from Word docs."""
    try:
        doc = Document(file_path)
        rules = []
        
        keywords = ["must", "always", "never", "should", "avoid", "ensure", "rule", "don't", "do not"]
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if len(text) < 20: continue # Skip short lines
            
            # Heuristic: Check for rule keywords
            if any(k in text.lower() for k in keywords):
                rules.append(text)
                
        return {
            "file": os.path.basename(file_path),
            "extracted_rules": rules
        }
    except Exception as e:
        return {"file": os.path.basename(file_path), "error": str(e)}

import numpy as np
from datetime import datetime, date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def main():
    extracted_data = {
        "case_studies": [],
        "audits": []
    }
    
    # Process Excel Files (Case Studies)
    excel_files = glob.glob(os.path.join(BASE_DIR, "*.xlsx"))
    for f in excel_files:
        if "~$" in f: continue # Skip temp files
        print(f"Processing Excel: {os.path.basename(f)}")
        data = extract_excel_patterns(f)
        extracted_data["case_studies"].append(data)
        
    # Process Docx Files (Audits/Transcripts)
    docx_files = glob.glob(os.path.join(BASE_DIR, "*.docx"))
    for f in docx_files:
        if "~$" in f: continue
        print(f"Processing Docx: {os.path.basename(f)}")
        data = extract_docx_rules(f)
        extracted_data["audits"].append(data)
        
    # Save to JSON
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(extracted_data, f, indent=2, cls=CustomJSONEncoder)
        
    print(f"Extraction complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
