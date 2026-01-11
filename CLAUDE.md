# mb-keyword-analysis Plugin

## Plugin Setup (CRITICAL)

This plugin provides Google Ads services. **To use any service, you MUST set up the Python path first.**

**Step 1: Find the plugin root**
```python
import sys
from pathlib import Path

# Option A: If you know the cache path
PLUGIN_ROOT = Path.home() / ".claude/plugins/cache/mb-plugins/mb-keyword-analysis/1.3.0"

# Option B: Find it dynamically (if running from within plugin)
# PLUGIN_ROOT = Path(__file__).parent.parent.parent  # adjust based on depth

sys.path.insert(0, str(PLUGIN_ROOT))
```

**Step 2: Import and use services**
```python
from backend.services.keyword_planner import KeywordPlannerService
from backend.services.google_sheets import GoogleSheetsService
# etc.
```

**Credentials:** Auto-loaded from `~/.mondaybrew/.env`. Required variables:
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- `GOOGLE_ADS_CUSTOMER_ID`

**Data Authenticity:** Keyword results include `_source: "google_ads_api"` to prove data is real.

---

## Critical Rules

1. **ALWAYS query MCP RAG before starting** - Use `query_knowledge()`, `get_methodology()`, or `get_example()`
2. **ALWAYS fetch the client's website** before keyword research
3. **NEVER use browser automation** when direct API access exists
4. **Ad Copy Pinning**: When using `{LOCATION(City):fallback}` in Headline 2, **pin H2 to position 2**
5. **ROI Calculator Tab**: ALWAYS use `scripts/add_roi_tab.py` - NEVER manually create Tab 4

---

## Available Services

### 1. Keyword Planner API
**File:** `backend/services/keyword_planner.py`

Generate keyword ideas and historical metrics from Google Ads Keyword Planner.

```python
from backend.services.keyword_planner import KeywordPlannerService

kp = KeywordPlannerService()

# Method 1: Website URL seed
results = kp.generate_keyword_ideas(
    page_url="https://client-website.dk",
    location_ids=[2208],  # Denmark
    language_id="1009"    # Danish
)

# Method 2: Keyword seeds
results = kp.generate_keyword_ideas(
    keywords=["brudekjole", "bryllup kjole"],
    location_ids=[2208],
    language_id="1009"
)

# Historical metrics
metrics = kp.get_historical_metrics(
    keywords=["brudekjole", "festkjole"],
    location_id=2208
)
```

**Location IDs:** Denmark `2208`, Norway `2578`, Sweden `2752`, Copenhagen `1020424`
**Language IDs:** Danish `1009`, Norwegian `1012`, Swedish `1015`, English `1000`

### 2. Google Sheets API
**File:** `backend/services/google_sheets.py`

```python
from backend.services.google_sheets import GoogleSheetsService

gs = GoogleSheetsService()

# Read
data = gs.read_sheet(spreadsheet_id="...", sheet_name="Keywords", range="A1:F100")

# Write
gs.write_to_sheet(spreadsheet_id="...", sheet_name="Sheet1", data=[["A", "B"], [1, 2]], start_cell="A1")
```

### 3. Google Ads Connector
**File:** `backend/services/ads_connector.py`

Full read/write access to Google Ads accounts.

**Read:** campaigns, ad groups, keywords, ads, search terms, geo performance, etc.
**Write:** create/update campaigns, ad groups, keywords, RSAs (with pinning), extensions.

**Safety:** Use `validate_only=True` for dry-runs on production accounts.

### 4. Search Console API
**File:** `backend/services/search_console.py`

```python
from backend.services.search_console import SearchConsoleService

sc = SearchConsoleService()
data = sc.get_search_analytics(
    site_url="https://client-website.dk",
    start_date="2024-01-01",
    end_date="2024-12-31",
    dimensions=["query"],
    row_limit=1000
)
```

### 5. GA4 API
**File:** `backend/services/ga4_service.py`

```python
from backend.services.ga4_service import GA4Service

ga4 = GA4Service()
props = ga4.list_properties()
behavior = ga4.get_behavior_metrics(property_id, days=30)
```

### 6. GTM API
**File:** `backend/services/gtm_service.py`

```python
from backend.services.gtm_service import GTMService

gtm = GTMService()
accounts = gtm.list_accounts()
containers = gtm.list_containers(accounts[0]['path'])
```

### 7. BigQuery
**File:** `backend/services/bigquery_manager.py`

```python
from backend.services.bigquery_manager import BigQueryManager

bq = BigQueryManager()
results = bq.client.query("SELECT ...").result()
```

### 8. RAG Engine
**File:** `backend/services/rag_engine.py`

```python
from backend.services.rag_engine import RAGEngine

rag = RAGEngine()
results = rag.query(query_text="How to structure ad groups?", n_results=5)
```

**Preferred:** Use MCP tools instead: `query_knowledge()`, `get_methodology()`, `get_example()`

---

## MCP RAG Tools

Available via MCP (no Python import needed):
- `query_knowledge(query, n_results=10, content_type=None, topic=None)`
- `get_methodology(task_type)` - "keyword_research", "ad_copy", "campaign_structure", "audit"
- `get_example(client_name)` - "spacefinder", "karim_design"
- `get_deliverable_schema(schema_type)` - "all", "keyword_analysis", "campaign_structure", "ad_copy", "roi_calculator"

---

## Deliverable Format

Every deliverable = Google Sheet with 3 tabs (+ optional Tab 4):

1. **Keyword Analysis** - `schemas/keyword_analysis.schema.json`
2. **Campaign Structure** - `schemas/campaign_structure.schema.json`
3. **Ad Copy** - `schemas/ad_copy.schema.json`
4. **ROI Beregner** (optional) - `schemas/roi_calculator.schema.json`

**Tab 4 - SCRIPT ONLY:**
```bash
python scripts/add_roi_tab.py SPREADSHEET_ID "Client Name"
```
Never create Tab 4 manually - the script handles colors, formulas, formatting.

---

## Keyword Research Methodology

### Phase 1: Understand the Business
- Fetch and read the website thoroughly
- Ask for constraints: budget, geo targeting, language, focus/exclusions

### Phase 2: Iterative Research
- Start with `page_url` seed
- Iterate with keyword seeds from high-volume themes
- Explore dimensions dynamically (service × location, product × intent, etc.)

### Phase 3: Categorization
**Match Types:**
- Exact `[keyword]` - high-intent, specific phrases
- Phrase `"keyword"` - most keywords
- Broad - discovery only, rarely used

**Ad Group Naming:** `{Theme} | {Location}`

**Negative Keywords:** gratis, billig, selv, DIY, hjemme, online + client-specific

### Phase 4: Campaign Structure
**Naming:** `mb | {LANG} | {Type} | {Theme}`

### Phase 5: RSA Ad Copy
- Headlines: 10-15, max 30 chars, **sentence case only**
- Descriptions: 4, max 90 chars
- Include location in 2-3 headlines for local businesses

---

## Reference Examples

- `knowledge_base/Data Examples/[KEYWORD ANALYSIS & AD COPY] - Spacefinder.xlsx` - 308 keywords, 21 ad groups
- `knowledge_base/Data Examples/[KEYWORD ANALYSIS & AD COPY] - Karim Design.xlsx` - wedding focus
- `knowledge_base/keyword research rag.md` - full methodology

---

## Common Mistakes

❌ Single-pass research
❌ Wrong language_id
❌ Generic keywords not specific to business
❌ Camel case in ad copy ("Professionel Ørevoks" - WRONG)
❌ Using browser automation when API exists
❌ Manually creating ROI tab

✅ Multiple iterations until comprehensive
✅ Correct language_id
✅ Business-specific keywords from website
✅ Sentence case ("Professionel ørevoks" - CORRECT)
✅ Direct API access
✅ Script for Tab 4
