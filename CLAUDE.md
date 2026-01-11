# Google Ads AI Assistant Playbook

## Overview
You are helping Monday Brew (mb) create Google Ads campaigns. This playbook ensures consistent, high-quality keyword research and campaign structure.

---

## Critical Rules

1. **ALWAYS query MCP RAG before starting any task** - Use `query_knowledge()`, `get_methodology()`, or `get_example()` first
2. **ALWAYS fetch and understand the client's website** before keyword research
3. **NEVER use browser automation** when direct API access exists
4. **Ad Copy Pinning**: When using `{LOCATION(City):fallback}` in Headline 2, **pin H2 to position 2**
5. **ROI Calculator Tab**: ALWAYS use `scripts/add_roi_tab.py` - NEVER manually create Tab 4. See `/schemas/README.md` for complete specification.

---

## Available Tools & APIs

**CRITICAL:** You have direct Python API access to these services. DO NOT use browser automation (Playwright/Chrome DevTools) when direct API access exists.

### 0. Google Ads API Connector (core toolbox)
**Location:** `/backend/services/ads_connector.py`

**What it does:** Full read + write access to Google Ads for audits and campaign management. This is the main toolbox the agent should use after strategy is decided via RAG.

- Read helpers (used by scripts like `scripts/audit_account.py`):
  - Account & structure: campaigns, ad groups, keywords, ads, assets
  - Performance: search terms, geo, devices, demographics, audiences, impression share, landing pages, click data, paid vs organic, auction insights
  - Config: budgets, bidding strategies, conversion actions, change history, recommendations
- Write helpers (all support `validate_only=True` and should default to dry-run unless explicitly overridden):
  - Campaigns & budgets: create/update campaigns (including Smart Bidding strategies), create/update budgets, remove campaigns
  - Ad groups & keywords: create ad groups, update status/bids, add/update/remove keywords, manage negatives and shared negative lists
  - Ads: create Responsive Search Ads (with pinning support for headlines/descriptions), update ad status
  - Assets & extensions: upload image assets, create/attach sitelinks, callouts, structured snippets, call assets, lead form assets
  - Conversions & audiences: upload offline conversions, attach audiences to campaigns/ad_groups, read audience performance

**Safety rules:**
- Prefer running write operations with `validate_only=True` first, especially on production accounts.
- Use the test account (`591-242-2766`) with `scripts/test_ads_manager.py` for live mutation tests where possible.
- Always decide *what* to do using RAG + methodology first, then call AdsConnector methods as the *how*.

### 1. Keyword Planner API
**Location:** `/backend/services/keyword_planner.py`

**What it does:** Generate keyword ideas and get historical search metrics from Google Ads Keyword Planner.

**How to use:**
```python
from backend.services.keyword_planner import KeywordPlannerService

kp = KeywordPlannerService()

# Method 1: Use website URL as seed
results = kp.generate_keyword_ideas(
    page_url="https://client-website.dk",
    location_ids=[2208],  # Denmark
    language_id="1009"    # Danish
)

# Method 2: Use keyword seeds
results = kp.generate_keyword_ideas(
    keywords=["brudekjole", "bryllup kjole"],
    location_ids=[2208],
    language_id="1009"
)

# Get historical metrics for specific keywords
metrics = kp.get_historical_metrics(
    keywords=["brudekjole", "festkjole"],
    location_id=2208
)
```

**Common location_ids:**
- Denmark: `2208`
- Norway: `2578`
- Sweden: `2752`
- Copenhagen: `1020424` (city-level targeting)

**Common language_ids:**
- Danish: `1009`
- Norwegian: `1012`
- Swedish: `1015`
- English: `1000`

### 2. Google Sheets API
**Location:** `/backend/services/google_sheets.py`

**What it does:** Read from and write to Google Sheets without browser automation.

**How to use:**
```python
from backend.services.google_sheets import GoogleSheetsService

gs = GoogleSheetsService()

# Read data from a sheet
spreadsheet_id = "1V7esYPSAzWWsuQSK-eeGywUKSJ16A1Ei"
data = gs.read_sheet(
    spreadsheet_id=spreadsheet_id,
    sheet_name="Keywords",
    range="A1:F100"
)

# Write data to a sheet
gs.write_to_sheet(
    spreadsheet_id=spreadsheet_id,
    sheet_name="Sheet3",
    data=[
        ["Ad Group", "Headlines", "Descriptions"],
        ["Brudekjole | København", "...", "..."]
    ],
    start_cell="A1"
)
```

**You have full access to Google Drive and all sheets in the user's Drive.**

### 3. Search Console API
**Location:** `/backend/services/search_console.py`

**What it does:** Get organic search data from Google Search Console (queries, impressions, clicks, CTR).

**How to use:**
```python
from backend.services.search_console import SearchConsoleService

sc = SearchConsoleService()

# Get search analytics data
data = sc.get_search_analytics(
    site_url="https://client-website.dk",
    start_date="2024-01-01",
    end_date="2024-12-31",
    dimensions=["query"],
    row_limit=1000
)
```

### 4. Google Analytics 4 API
**Location:** `/backend/services/ga4_service.py`

**What it does:** Uses OAuth (the shared Google Ads OAuth client + `GOOGLE_ADS_REFRESH_TOKEN`) to act as your user, list GA4 accounts/properties/data streams, and run read-only GA4 reports for any property your user can access. No service-account access management is required.

**Auth details:**
- Reuses `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, and `GOOGLE_ADS_REFRESH_TOKEN` (generated by `scripts/get_master_token.py`).
- Requires the refresh token to include `https://www.googleapis.com/auth/analytics.readonly` and `https://www.googleapis.com/auth/analytics.edit`.
- GA4Service sees the same GA4 Accounts/Properties that the authenticated user sees.

**How to use:**
```python
from backend.services.ga4_service import GA4Service

ga4 = GA4Service()

# 1) List all accessible GA4 properties (across accounts)
props = ga4.list_properties()
# props -> [{"property_id": "123456789", "display_name": "...", "account_name": "..."}, ...]

# 2) Optionally map a website domain to a GA4 property
matches = ga4.find_properties_by_domain("client-website.dk")

if matches:
    property_id = matches[0]["property_id"]
else:
    property_id = props[0]["property_id"]

# 3) Fetch behavior & conversions
behavior = ga4.get_behavior_metrics(property_id, days=30)
conversions = ga4.get_conversion_breakdown(property_id, days=30)
top_pages = ga4.get_top_pages(property_id, days=30, limit=100)
traffic_sources = ga4.get_traffic_sources(property_id, days=30, limit=100)
```

### 5. Google Tag Manager API
**Location:** `/backend/services/gtm_service.py`

**What it does:** Uses OAuth to list GTM accounts, containers, workspaces, and tags.

**How to use:**
```python
from backend.services.gtm_service import GTMService

gtm = GTMService()

# 1) List accounts
accounts = gtm.list_accounts()
# accounts -> [{"account_id": "...", "name": "...", "path": "accounts/123"}, ...]

# 2) List containers
containers = gtm.list_containers(accounts[0]['path'])
# containers -> [{"container_id": "...", "name": "...", "path": "accounts/123/containers/456"}, ...]

# 3) List workspaces
workspaces = gtm.list_workspaces(containers[0]['path'])

# 4) List tags
tags = gtm.list_tags(workspaces[0]['path'])
```

### 6. BigQuery API
**Location:** `/backend/services/bigquery.py`

**What it does:** Query BigQuery datasets (useful for large-scale analytics, historical data).

**How to use:**
```python
from backend.services.bigquery import BigQueryService

bq = BigQueryService()

# Run a query
results = bq.query("""
    SELECT keyword, SUM(impressions) as total_impressions
    FROM `project.dataset.table`
    WHERE date >= '2024-01-01'
    GROUP BY keyword
    ORDER BY total_impressions DESC
    LIMIT 100
""")
```

### 7. RAG Engine (ChromaDB)
**Location:** `/backend/services/rag_engine.py`

**What it does:** Semantic search over the knowledge base (methodology, examples, best practices).

**How to use:**
```python
from backend.services.rag_engine import RAGEngine

rag = RAGEngine()

# Search for relevant content
results = rag.query(
    query_text="How should I structure ad groups for wedding dresses?",
    n_results=5
)
```

### 8. MCP RAG Server (Google Ads RAG Knowledge)
**Location:** `mcp-servers/google-ads-rag/server.py`

**What it does:** Semantic search over the agency's knowledge base and access to strict output schemas. Supports metadata filters and agency boosting.

**MCP Tools:**
- `query_knowledge(query, n_results=10, content_type=None, topic=None, boost_agency=True)`
- `get_methodology(task_type)` - For keyword_research, ad_copy, campaign_structure, audit
- `get_example(client_name)` - e.g., "spacefinder", "karim_design"
- `get_deliverable_schema(schema_type)` - "all", "keyword_analysis", "campaign_structure", "ad_copy", "roi_calculator"

**Content types:** `methodology`, `case_study`, `example`, `warning`, `best_practice`

**Deliverable Format (CRITICAL)**

Every Google Ads deliverable must follow the 3-tab schema (with optional Tab 4):

1. **Before creating output**: Call `get_deliverable_schema("all")` to get the exact format
2. **Create a Google Sheet** with 3 tabs: Keyword Analysis, Campaign Structure, Ad Copy
3. **Follow the golden examples** in `/schemas/README.md`
4. **After creating output**: Validate using the schemas

Schema location: `/schemas/`
- `keyword_analysis.schema.json`
- `campaign_structure.schema.json`
- `ad_copy.schema.json`
- `roi_calculator.schema.json` (optional Tab 4)
- `README.md` (golden examples)

**Tab 4: ROI Beregner (CRITICAL - Use Script Only)**

⚠️ **NEVER create Tab 4 manually. ALWAYS use the script.**

```bash
# Add ROI tab to existing sheet
python scripts/add_roi_tab.py SPREADSHEET_ID "Client Name"
```

**Why script-only?**
- Manual creation produces broken output (no colors, wrong structure, missing formulas)
- The script ensures: exact colors (RGB values), column widths, formulas, conditional formatting
- Client-facing deliverable - must look professional

**For complete specification see:** `/schemas/README.md` (Tab 4 section)

**Quick reference:**
- Row 4: Blue header `📊 DINE TAL` - RGB(64,115,179)
- Row 9: Teal header `📈 KAMPAGNE ESTIMATER` - RGB(51,128,128)
- Row 13: Green header `🧮 BEREGNEDE RESULTATER` - RGB(51,140,89)
- Yellow input cells (B5:B7, B10:B11)
- Conditional formatting on Row 18 (profit cell): Green if >0, Red if ≤0

### 9. WebFetch
**Built-in tool:** Use this to fetch and analyze website content.

**How to use:**
```python
# Fetch website to understand business
content = fetch_url("https://client-website.dk")
```

---

## Phase 1: Understand the Business (CRITICAL)

**Don't skip this.** The biggest mistake is doing generic keyword research without understanding the ACTUAL business.

1. **Fetch and read the client's website thoroughly**
   - What services do they ACTUALLY offer?
   - What makes them unique?
   - Are there specific products/services to focus on?
   - Are there specific products/services to EXCLUDE?

2. **Ask the user for constraints**
   - Budget (daily/monthly)
   - Geographic targeting (city, radius, national?)
   - Language (Danish, Norwegian, Swedish, etc.)
   - Any specific focus areas?
   - Any exclusions? (Example: Karim Design = wedding dresses ONLY, not party dresses)

**Example mistake:** For Helene's Høreklinik, I did generic "hearing clinic" research and missed "høreværn" (custom hearing protection, 3,600 monthly searches) - a major service they offer.

## Phase 2: Iterative Keyword Research

**Use the Keyword Planner API multiple times. Not once. Multiple times.**

### API Details
Location: `/backend/services/keyword_planner.py`

```python
generate_keyword_ideas(
    keywords=None,        # List of seed keywords
    page_url=None,        # OR use the website URL as seed
    location_ids=None,    # [2208] for Denmark, [2578] for Norway
    language_id="1009"    # 1009=Danish, 1012=Norwegian, 1000=English
)
```

### Research Strategy

1. **Start with page_url seed**
   ```python
   # First pass: Let Google understand the business
   results = kp.generate_keyword_ideas(
       page_url="https://client-website.dk",
       location_ids=[2208],
       language_id="1009"
   )
   ```

2. **Iterate with keyword seeds**
   - Extract high-volume themes from first pass
   - Run targeted searches for each theme
   - Cross-pollinate: service + location, service + intent, etc.

3. **Explore dimensions dynamically**
   - Some businesses are location × service (Companyons: Copenhagen/Aarhus × meeting rooms/offices)
   - Some are product × material (Karim Design: wedding dress × fitting/alteration)
   - Some are condition × treatment (Helene's: earwax × removal, hearing × test, hearing protection × custom)

   **Don't hardcode dimensions.** Discover them from the business.

### Quality Targets

**Find ALL relevant keywords for the business.**

Don't worry about hitting arbitrary numbers. A small local business with one service might legitimately have 20 good keywords. A large multi-location business might have 300+. The goal is comprehensive coverage of what people actually search for, based on:
- Available search volume in the market
- The business's actual service offerings
- Budget constraints (no point having 500 keywords for a 100 DKK/day budget)

If you're only finding 15 keywords and the business clearly offers more services, you're probably not iterating enough.

## Phase 3: Keyword Filtering and Categorization

### Match Type Rules (from RAG)

1. **Exact Match `[keyword]`** - Use for:
   - Highly specific phrases (e.g., `[bridal gown alteration copenhagen]`)
   - Low-volume high-intent terms
   - Protecting against broad interpretation

2. **Phrase Match `"keyword"`** - Use for:
   - Medium specificity (e.g., `"brudekjole"`)
   - Most keywords should be phrase match

3. **Broad Match** - Use sparingly:
   - Only for discovery campaigns
   - Not recommended for most clients

### Categorization

Group keywords into ad groups by:
- **Service/Product** (e.g., "Ørevoks Fjernelse", "Høretest", "Brudekjole")
- **Location** if multi-location (e.g., "København", "Aarhus")
- **Intent** (e.g., "Book", "Price", "Near Me")

**Ad Group Naming:** `{Theme} | {Location}`
- Example: "Brudekjole | København"
- Example: "Ørevoks Fjernelse | Valby"

### Negative Keywords

Build a negative keyword list:
- **Common negatives:** gratis, billig, billige, selv, DIY, hjemme, online (if not online business)
- **Client-specific:** matas (for medical services), fest (if wedding-only)

## Phase 4: Campaign Structure

### Naming Convention
`mb | {LANG} | {Type} | {Theme}`

Examples:
- `mb | DA | Search | Høreklinik Valby`
- `mb | DA | Radius | Brudekjoler`
- `mb | NO | Search | Kontorleie`

### URL Strategy

- Use the most specific landing page possible
- Example: Don't use homepage if there's a service-specific page
- Example: `https://spacefinder.no/kontorer/til-leie/bergen/` (not homepage)

## Phase 5: RSA Ad Copy

### Headlines (10-15 required)
- Max 30 characters each
- **ALWAYS use sentence case** - Only capitalize first letter, not every word
- Mix of:
  - Service/product names: "Professionel ørevoks fjernelse"
  - Location: "Book tid i Valby nu"
  - CTA: "Ring til os i dag"
  - Benefits: "Hurtig ørevoksbehandling"
  - Trust: "Personlig og varm service"

### Descriptions (4 required)
- Max 90 characters each
- Expand on benefits, process, USPs

### Language
- Match the target market language
- Use natural, conversational copy
- Include location in at least 2-3 headlines for local businesses

## Phase 6: Output Format

### Required Files

1. **Keywords CSV**
   - Columns: keyword, volume, match_type, ad_group, intent, url
   - Example: `client_keywords_final.csv`

2. **Ads JSON**
   - Structure:
   ```json
   [
     {
       "Campaign": "mb | DA | Search | Theme",
       "Ad Group": "Service | Location",
       "Headline 1": "Headline text...",
       "Headline 2": "Headline text...",
       "...": "...",
       "Headline 15": "Headline text...",
       "Description 1": "Description text...",
       "Description 2": "Description text...",
       "Description 3": "Description text...",
       "Description 4": "Description text...",
       "Path 1": "Path1",
       "Path 2": "Path2",
       "Final URL": "https://..."
     }
   ]
   ```

3. **Full Analysis JSON**
   - Campaign structure
   - Budget estimates
   - Negative keywords
   - Total volume

## Reference Examples

**Study these before starting:**

1. **Spacefinder** (`/knowledge_base/Data Examples/[KEYWORD ANALYSIS & AD COPY] - Spacefinder.xlsx`)
   - 308 keywords, 21 ad groups
   - Norwegian language
   - Location-specific URLs
   - Gold standard output

2. **Karim Design** (`/knowledge_base/Data Examples/[KEYWORD ANALYSIS & AD COPY] - Karim Design.xlsx`)
   - Existing client, wedding-only focus
   - Includes misspellings: "brudkjole" (8,100 vol)
   - Booking intent: "prøve brudekjole"

3. **RAG Content** (`/knowledge_base/keyword research rag.md`)
   - 200+ lines of agency methodology
   - Match type rules
   - Negative keyword frameworks

## Critical Lessons

1. **Always read the actual website** - Don't assume generic services
2. **Iterate multiple times** - One API call is never enough
3. **Ask about constraints** - Wedding-only? Local-only? Budget?
4. **Look for low-hanging fruits** - High-volume keywords specific to their business
5. **Use examples as templates** - Don't reinvent the output format

## Common Mistakes to Avoid

❌ Single-pass research (only 15 keywords when business offers more)
❌ Wrong language (English instead of Danish)
❌ Generic keywords (not specific to the business)
❌ Missing obvious high-volume terms (like "høreværn" for hearing clinic)
❌ Placeholder headlines ("Professional Service Here")
❌ Generic URLs (homepage for everything)
❌ **Camel case in ad copy** ("Professionel Ørevoks Fjern" - WRONG)
❌ **Using browser automation when API access exists** (don't use Playwright for Google Sheets)
❌ **Manually creating ROI tab** (use `scripts/add_roi_tab.py` - no exceptions)

✅ Multiple iterations until comprehensive coverage
✅ Correct language_id for target market
✅ Business-specific keywords discovered from website
✅ Comprehensive coverage of ALL services
✅ Tailored ad copy in target language with sentence case
✅ Specific landing pages for each service
✅ **Sentence case in ad copy** ("Professionel ørevoks fjernelse" - CORRECT)
✅ **Use direct API access** (google_sheets.py, keyword_planner.py, etc.)
✅ **Use `scripts/add_roi_tab.py` for Tab 4** (guarantees consistent formatting)
