---
description: Run full keyword analysis workflow for a client website
argument-hint: <website-url>
allowed-tools: WebFetch, Read, Write, Bash, AskUserQuestion, TodoWrite
---

# Keyword Analysis Workflow

Complete Google Ads campaign planning workflow in 7 phases. Each phase produces a clear artifact. **Do not skip phases.**

## Target URL
@$ARGUMENTS

## Output Directory
Create artifacts in: `clients/{client-name}/`
Extract client name from the website URL (e.g., `aeflyt.dk` → `clients/aeflyt/`)

---

## CRITICAL RULES

1. **Never skip Phase 1** - Business understanding blocks everything else
2. **Never do single-pass research** - Phase 3 requires multiple API iterations
3. **Never default all keywords to Phrase match** - Apply match type rules
4. **Always use sentence case in ad copy** - Not Title Case
5. **Always use specific landing pages** - Never homepage for everything
6. **Currency must match target market** - DKK for Denmark, NOK for Norway, SEK for Sweden

---

## Phase Overview

| Phase | Output Artifact | Gate |
|-------|-----------------|------|
| 1. Business Understanding | `website_content.md` | BLOCKS Phase 2 |
| 2. Strategic Analysis | `potential_analysis.md` | BLOCKS Phase 3 |
| 3. Keyword Research | `keyword_analysis.json` | BLOCKS Phase 4 |
| 4. Campaign Structure | `campaign_structure.json` | BLOCKS Phase 5 |
| 5. Ad Copy | `ad_copy.json` | BLOCKS Phase 6 |
| 6. ROI Projection | `roi_calculator.json` | BLOCKS Phase 7 |
| 7. Presentation | `presentation.html` | Final |

---

## Phase 1: Business Understanding

**Gate:** This phase MUST complete before any keyword research begins.

### Actions

1. **Fetch the client website** using WebFetch
   - Homepage
   - All service/product pages
   - About page
   - Contact page

2. **Extract key information:**
   - All services/products offered
   - Primary vs secondary services (prioritize)
   - Geographic focus (local, regional, national?)
   - Target customer type (B2B, B2C, both?)
   - Unique selling propositions (USPs)
   - Key messaging and brand voice
   - Existing landing page URLs and structure

3. **Identify exclusions** - What NOT to target
   - Example: Wedding dress shop that does NOT do party dresses
   - Example: Copenhagen-only business, NOT national

4. **Gather discovery information from user** using AskUserQuestion:
   - What does a typical customer spend (first purchase or annual value)?
   - Which 1-3 services should Google Ads focus on?
   - What is the monthly Google Ads budget?
   - What geographic area should we target (city, radius, national)?
   - What language (Danish, Norwegian, Swedish, English)?
   - What counts as a successful conversion (form, call, purchase, demo)?
   - Have you run Google Ads before, and what happened?
   - Who do you actually lose customers to (competitors)?
   - Is there anything we should NOT target (services, locations, customer types)?
   - Any meeting notes, transcripts, or additional context?
   - List ALL services you want to advertise via Google Ads (be specific)?
   - Any services you DON'T want to advertise or don't offer?

### Output Artifact: `website_content.md`

Must include:
- Core services list
- Key messaging
- Target customers
- USPs
- Landing page URLs
- Exclusions
- **Canonical Service List** (from Q9 - services to advertise with Service IDs)
- **Services NOT Offered** (from Q10 - for negative keyword generation)

### Checkpoint

Before proceeding to Phase 2, verify:
- [ ] Website has been fetched and analyzed
- [ ] All services/products are documented
- [ ] User constraints have been gathered
- [ ] Exclusions are documented
- [ ] **Services to advertise listed (from AskUserQuestion)**
- [ ] **Services NOT to advertise listed (from AskUserQuestion)**
- [ ] **Canonical Service List created with Service IDs**

If any checkbox is incomplete: **STOP. Do not proceed.**

---

## Phase 2: Strategic Analysis

**Prerequisite:** Phase 1 `website_content.md` must exist.

### Actions

1. **Synthesize Phase 1** into strategic document
2. **Identify keyword categories** based on services
3. **Define campaign segmentation rationale**
   - What warrants separate campaigns?
   - B2B vs B2C split?
   - Geographic split?
4. **Outline ad copy strategy** (tone, key messages)
5. **Project ROI** (rough estimate before data)

### Output Artifact: `potential_analysis.md`

Structure:
1. Executive Summary
2. Website & Service Audit
3. Keyword Analysis Summary (categories, not data yet)
4. Proposed Campaign Structure
5. Ad Copy Strategy
6. ROI Projection (preliminary)
7. Next Steps

### Checkpoint

Before proceeding to Phase 3, verify:
- [ ] Strategic analysis document complete
- [ ] Campaign segmentation defined
- [ ] All services have assigned keyword categories

---

## Phase 3: Keyword Research

**Prerequisite:** Phase 2 `potential_analysis.md` must exist.

**CRITICAL:** This is iterative. NOT single-pass.

### Actions

1. **Pass 1: URL Seed**
   ```python
   from backend.services.keyword_planner import KeywordPlannerService
   kp = KeywordPlannerService()

   results = kp.generate_keyword_ideas(
       page_url="https://client-website.dk",
       location_ids=[2208],  # Denmark
       language_id="1009"    # Danish
   )
   ```
   Extract themes from results.

2. **Pass 2: Theme Seeds**
   For each theme discovered in Pass 1:
   ```python
   results = kp.generate_keyword_ideas(
       keywords=["theme keyword 1", "theme keyword 2"],
       location_ids=[2208],
       language_id="1009"
   )
   ```

3. **Pass 3: Cross-Pollination**
   Combine dimensions:
   - Service + location: "flyttefirma københavn"
   - Service + intent: "flyttefirma pris"
   - Service + modifier: "billig flyttefirma"

4. **Pass 4: Variations**
   - Misspellings (common ones)
   - Plural/singular
   - Long-tail variations

5. **Apply Match Type Rules**
   - **Exact `[keyword]`:** High-intent + specific + low-volume
   - **Phrase `"keyword"`:** Medium specificity + good volume
   - **Broad:** Discovery campaigns only (use sparingly)

6. **Tag Each Keyword**
   - Category: Service bucket from Phase 2
   - Intent: High / Medium / Low
   - Include: true / false

### Stop Criteria

Stop iterating when:
- All services from Phase 1 have keyword coverage
- Location variants exist (for geo businesses)
- No new themes emerging from seeds

### Service Validation (Phase 3.5)

**CRITICAL:** Before finalizing keywords, validate against Canonical Service List.

1. **Map each keyword to a Service ID** from the Canonical Service List
2. **Flag mismatches** - keywords that don't match any service you offer
3. **Ask user** about any flagged keywords using AskUserQuestion:
   - "I found keywords for [LinkedIn/TikTok/etc] but this isn't in your services list. Should I exclude these?"
4. **Mark excluded keywords** with `"Include": false` and `"Exclusion_Reason": "Service not offered"`

Example: If canonical services are "Google Ads, Meta Ads, Lead Generation" but keyword research returns "linkedin annoncering" → FLAG and confirm exclusion.

### Output Artifact: `keyword_analysis.json`

Format:
```json
[
  {
    "Keyword": "flyttefirma",
    "Avg. Monthly Searches": 8100,
    "Competition": "High",
    "Top of page bid (low range)": "DKK 19.00",
    "Top of page bid (high range)": "DKK 65.74",
    "Category": "Erhvervsflytning",
    "Intent": "High",
    "Include": true
  }
]
```

**Currency MUST match target market.** DKK for Denmark. NOK for Norway.

### Checkpoint

Before proceeding to Phase 4, verify:
- [ ] Multiple research passes completed (not single-pass)
- [ ] All services have keyword coverage
- [ ] Match types are varied (not all Phrase)
- [ ] Currency is correct for target market
- [ ] Category and Intent tags applied
- [ ] **Service Validation complete (Phase 3.5)**
- [ ] **Mismatched keywords flagged and confirmed with user**
- [ ] **Excluded keywords marked with Include: false**

---

## Phase 4: Campaign Structure

**Prerequisite:** Phase 3 `keyword_analysis.json` must exist.

### Actions

1. **Map keywords to ad groups**
   - Group by service/product
   - Group by location (if geo campaign)
   - Keep ad groups tightly themed

2. **Apply naming conventions**

   **Campaign names:** `mb | {LANG} | {Type} | {Theme}`
   - `mb | DA | Search | Erhvervsflytning`
   - `mb | NO | Search | Kontor`
   - `mb | DA | Brand | Aeflyt`

   **Ad group names:** `{Theme} | {Location}`
   - `Erhvervsflytning | København`
   - `Privatflytning | Sjælland`

3. **Assign landing pages**
   - Use SPECIFIC pages, not homepage
   - Match landing page to ad group theme
   - Example: `/erhvervsflytning/` for business moving keywords

4. **Define match types per keyword**
   - Apply from Phase 3 analysis

### Output Artifact: `campaign_structure.json`

Format:
```json
[
  {
    "Campaign": "mb | DA | Search | Erhvervsflytning",
    "Ad Group": "Erhvervsflytning | København",
    "Keyword": "erhvervsflytning københavn",
    "Match Type": "Phrase",
    "Final URL": "https://aeflyt.dk/erhvervsflytning/"
  }
]
```

### Checkpoint

Before proceeding to Phase 5, verify:
- [ ] All keywords assigned to ad groups
- [ ] Campaign names follow `mb | LANG | Type | Theme`
- [ ] Landing pages are specific (not all homepage)
- [ ] Ad groups are tightly themed

---

## Phase 5: Ad Copy

**Prerequisite:** Phase 4 `campaign_structure.json` must exist.

### Actions

1. **Create RSAs for each ad group**

2. **Apply headline rules:**
   - 30 characters max
   - 6-10 quality headlines (NOT 15 padding)
   - **SENTENCE CASE** - "Kontor til leje i København"
   - NOT Title Case - "Kontor Til Leje I København"

3. **Apply DKI (Dynamic Keyword Insertion) in Headline 1:**
   ```
   {KeyWord:fallback text}
   ```
   Pin to position 1.

4. **Apply Location Insertion in Headline 2 (geo campaigns):**
   ```
   {LOCATION(City):fallback}
   ```
   Pin to position 2.

5. **Create descriptions:**
   - 90 characters max
   - 4 descriptions required
   - Expand on benefits, process, USPs

### Output Artifact: `ad_copy.json`

Format:
```json
[
  {
    "Campaign": "mb | DA | Search | Erhvervsflytning",
    "Ad Group": "Erhvervsflytning | København",
    "Headline 1": "{KeyWord:Erhvervsflytning i København}",
    "Headline 1 position": "1",
    "Headline 2": "Få et uforpligtende tilbud",
    "Headline 2 position": "",
    "Headline 3": "Flytning med kærlig hånd",
    "Headline 3 position": "",
    "Description 1": "Professionel erhvervsflytning på Sjælland. Hurtig og pålidelig service.",
    "Description 1 position": "",
    "Path 1": "erhverv",
    "Path 2": "flytning",
    "Final URL": "https://aeflyt.dk/erhvervsflytning/"
  }
]
```

### Checkpoint

Before proceeding to Phase 6, verify:
- [ ] Sentence case applied (not Title Case)
- [ ] 6-10 headlines per ad group
- [ ] DKI in Headline 1 with position 1 pinning
- [ ] 4 descriptions per ad group
- [ ] All URLs are specific landing pages

---

## Phase 6: ROI Projection

**Prerequisite:** Phase 5 `ad_copy.json` must exist.

### Actions

1. **Calculate projections based on:**
   - Budget (from Phase 1 constraints)
   - Average CPC (from Phase 3 keyword data)
   - Estimated conversion rate (3-5% default)
   - Estimated close rate (15-20% default for services)
   - Profit per customer (from user)

2. **For Google Sheets delivery:**
   Use the ROI script to ensure consistent formatting:
   ```bash
   python scripts/add_roi_tab.py <spreadsheet_id> --client-name "Client Name"
   ```

### Output Artifact: `roi_calculator.json`

Format:
```json
{
  "currency": "DKK",
  "budget": 5000,
  "cpc": 15,
  "conversion_rate": 5,
  "close_rate": 20,
  "profit_per_customer": 2000,
  "estimated_clicks": 333,
  "estimated_leads": 16,
  "estimated_customers": 3,
  "estimated_revenue": 6600,
  "roas": 1.32
}
```

**Note:** Rates should be integers (5 = 5%), not decimals (0.05). The presentation uses interactive sliders.

---

## Phase 7: Presentation

**Prerequisite:** Phase 6 `roi_calculator.json` must exist.

### Purpose

Generate a professional, interactive HTML presentation for client delivery. This is the final deliverable that:
- Presents the analysis in a beautiful, interactive dashboard
- Allows clients to explore keywords, campaigns, and ad copy
- Includes interactive ROI calculator with adjustable inputs
- Shows Google Ad previews of the proposed ads

### Actions

1. **Run the presentation generator script:**
   ```bash
   python scripts/generate_presentation.py clients/{client-name}
   ```

   Or with custom options:
   ```bash
   python scripts/generate_presentation.py clients/{client-name} \
       --name "Client Display Name" \
       --color "#2b74b8"
   ```

   The script path relative to the plugin is:
   `~/.claude/plugins/mb-marketplace/plugins/mb-keyword-analysis/scripts/generate_presentation.py`

2. **The script will:**
   - Read all JSON artifacts (keyword_analysis, campaign_structure, ad_copy, roi_calculator)
   - Extract executive summary from potential_analysis.md
   - Extract metadata from website_content.md
   - Generate an interactive Vue.js + Tailwind presentation

### Output Artifact: `presentation.html`

The presentation includes 5 interactive tabs:
1. **Executive Summary** - KPI cards, key findings, recommendations
2. **ROI Beregner** - Interactive calculator with sliders and funnel visualization
3. **Søgeordsanalyse** - Searchable, filterable keyword table with competition indicators
4. **Kampagnestruktur** - Visual campaign hierarchy with ad groups and keywords
5. **Annonceeksempler** - Google Ad previews showing how ads will appear

### Features

- **Interactive ROI Calculator**: Users can adjust budget, CPC, conversion rates
- **Keyword Search**: Filter keywords by text and category
- **Visual Indicators**: Competition levels with color-coded badges
- **Ad Previews**: Realistic Google Ad format with sitelinks

### Checkpoint

Before finalizing, verify:
- [ ] All 5 tabs are populated with data
- [ ] ROI calculator shows realistic projections
- [ ] Keyword table is searchable and filterable
- [ ] Ad previews correctly render DKI and location macros

---

## Final Delivery

After all phases complete:

1. **Local presentation:** `clients/{client-name}/presentation.html`
   - Open in browser: `file://path/to/clients/{client-name}/presentation.html`
   - This is the primary client deliverable

2. **Optional Google Sheet** with 4 tabs (for data export):
   - Tab 1: Keyword Analysis (from `keyword_analysis.json`)
   - Tab 2: Campaign Structure (from `campaign_structure.json`)
   - Tab 3: Ad Copy (from `ad_copy.json`)
   - Tab 4: ROI Beregner (use `scripts/add_roi_tab.py`)

3. **Run validation:**
   ```bash
   python scripts/validate_output.py <output_directory>
   ```

4. **Deliver to user** with:
   - Link to presentation.html (primary)
   - Link to Google Sheet (optional, for data access)

---

## Common Mistakes to Avoid

- Single-pass keyword research (only 15 keywords when business offers more)
- Wrong language_id (English instead of Danish)
- Generic keywords not specific to the business
- All match types set to Phrase (no differentiation)
- Title Case in ad copy ("Professional Service Here")
- Homepage URL for all landing pages
- Wrong currency (USD instead of DKK)
- Skipping business understanding phase
- **Including keywords for services not offered** (e.g., LinkedIn keywords when business only does Google/Meta)
- **Skipping service validation questions** (services to advertise / services NOT to advertise)
- **Not validating keywords against Canonical Service List**
