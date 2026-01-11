# Monday Brew Deliverable Schemas

This directory contains the JSON Schemas that enforce the structure of our Google Ads deliverables.

## The 3-Tab Architecture
Every deliverable must be a single Google Sheet with three specific tabs:

1.  **`Keyword Analysis`**: The research foundation.
2.  **`Campaign Structure`**: The implementation plan.
3.  **`Ad Copy`**: The final creative.

---

## Tab 1: Keyword Analysis
**Schema**: `keyword_analysis.schema.json`
**Purpose**: Prove the data-driven basis for the campaign.

### Currency Formatting (CRITICAL)

The Keyword Planner API returns bids in **account currency** (often USD), NOT target geo currency.

**Format for target market:**
- Denmark: `DKK 4.23` or just `4.23` (no USD)
- Norway: `NOK 45.00` or just `45.00`
- Sweden: `SEK 42.00` or just `42.00`

**Never deliver USD values to Danish/Norwegian/Swedish clients.**

### Golden Example (from AHH Planning)
```json
[
  {
    "Keyword": "Bryllups planlægger",
    "Avg. Monthly Searches": 50,
    "YoY Change": "-0.29",
    "Competition": "Low",
    "Top of page bid (low range)": "DKK 4.23",
    "Top of page bid (high range)": "DKK 9.91",
    "Category": "Wedding Planner",
    "Intent": "High",
    "Include": true
  }
]
```

---

## Tab 2: Campaign Structure
**Schema**: `campaign_structure.schema.json`
**Purpose**: Map keywords to Ad Groups and Landing Pages.

### Golden Example (from Haus20)
```json
[
  {
    "Campaign": "mb | DA | Search | Kontor",
    "Ad Group": "Kontor | Gladsaxe",
    "Keyword": "Kontor til leje gladsaxe",
    "Match Type": "Phrase",
    "Final URL": "https://work.haus20.dk/gladsaxe"
  }
]
```

---

## Tab 3: Ad Copy
**Schema**: `ad_copy.schema.json`
**Purpose**: Final RSA creative ready for Google Ads Editor upload.

### CRITICAL RULES

1. **Keyword Insertion in Headline 1**:
   - SHOULD use `{KeyWord:fallback text}` syntax for tightly themed ad groups
   - Pin to position 1 when using DKI
   - Example: `{KeyWord:Kontor til leje i Bergen}`
   - **Skip DKI for**: Brand campaigns, competitor campaigns, mixed-intent groups, or when keywords would truncate (>30 chars)

2. **Location Insertion in Headline 2** (for geo campaigns):
   - SHOULD use `{LOCATION(City):fallback}` syntax
   - Pin to position 2
   - Example: `Utforsk kontorer i {LOCATION(City):din by}`

3. **Position Columns**:
   - Every headline has a corresponding position column
   - Only pin H1 (position 1) and optionally H2 (position 2)
   - Leave other positions BLANK to let Google rotate

4. **Headline Count**:
   - Use 6-10 high-quality headlines, NOT all 15
   - Each headline must add unique value
   - Redundant headlines hurt ad strength

5. **Sentence Case**:
   - Correct: `Kontor til leje i København`
   - Incorrect: `Kontor Til Leje I København`

### Golden Example (from Spacefinder - THE NORTH STAR)

**National Campaign with Location Insertion:**
```csv
Campaign,Ad Group,Headline 1,Headline 1 position,Headline 2,Headline 2 position,Headline 3,Headline 3 position,Headline 4,Headline 4 position,Headline 5,Headline 5 position,Headline 6,Headline 6 position,Headline 7,Headline 7 position,Description 1,Description 1 position,Description 2,Description 2 position,Description 3,Description 3 position,Description 4,Description 4 position,Path 1,Path 2,Final URL
mb | NO | Search | Kontor,Kontor | Øvrige byer,{KeyWord:Finn kontor som passer deg},1,Utforsk kontor i {LOCATION(City):din by},2,Vi følger deg hele veien,,Finn kontoret i 3 Steg,,Norges største kontormarked,,Få kontorvalg på sekunder,,Få ekte kontoralternativer,,"Finn fleksible kontorer i {LOCATION(City):din by}, raskt og enkelt med anbefalinger fra Spacefinder.",,Spacefinder hjelper deg å finne ditt nye kontor skreddersydd for din bedrift.,,Book gratis rådgivning hos oss og finn det perfekte kontoret for deg og din bedrift.,,"Hos Spacefinder kan du sammenligne leiepriser og få anbefalinger, helt kostnadsfritt.",,kontor,leie,https://spacefinder.no/
```

**City-Specific Campaign (no location insertion needed):**
```csv
Campaign,Ad Group,Headline 1,Headline 1 position,Headline 2,Headline 2 position,Headline 3,Headline 3 position,Headline 4,Headline 4 position,Headline 5,Headline 5 position,Headline 6,Headline 6 position,Description 1,Description 1 position,Description 2,Description 2 position,Description 3,Description 3 position,Description 4,Description 4 position,Path 1,Path 2,Final URL
mb | NO | Search | Kontor,Kontor | Bergen,{KeyWord:Kontor til leie i Bergen},1,Vi følger deg hele veien,,Finn kontoret i 3 Steg,,Norges største kontormarked,,Få kontorvalg på sekunder,,Få ekte kontoralternativer,,"Finn fleksible kontorer i Bergen, raskt og enkelt med anbefalinger fra Spacefinder.",,Spacefinder hjelper deg å finne ditt nye kontor skreddersydd for din bedrift.,,Book gratis rådgivning hos oss og finn det perfekte kontoret for deg og din bedrift.,,"Hos Spacefinder kan du sammenligne leiepriser og få anbefalinger, helt kostnadsfritt.",,kontorer,bergen,https://spacefinder.no/kontorer/til-leie/bergen/
```

**Brand Campaign:**
```csv
Campaign,Ad Group,Headline 1,Headline 1 position,Headline 2,Headline 2 position,Headline 3,Headline 3 position,Headline 4,Headline 4 position,Headline 5,Headline 5 position,Headline 6,Headline 6 position,Headline 7,Headline 7 position,Headline 8,Headline 8 position,Headline 9,Headline 9 position,Description 1,Description 1 position,Description 2,Description 2 position,Description 3,Description 3 position,Description 4,Description 4 position,Path 1,Path 2,Final URL
mb | Brand | Spacefinder,Spacefinder,Spacefinder: Din Rådgiver,1,Norges Største Kontormarked,2,100% Gratis digital tjeneste,2,Hundrevis av ledige kontorer,2,Kontormarkedsplassen for SMB,3,Ekspert på kontor for din SMB,2,Start søket på få minutter,3,Få personlig kontormatch,3,Kontakt oss for rådgivning,3,Spacefinder er Norges største markedsplass for kontorlokaler. Tjenesten er 100% gratis.,,Få øyeblikkelig oversikt over kostnader. Start med vår raske og datadrevne matching.,,Vi er din digitale rådgiver. Sammenlign kontorer fra proffe utleiere i 3 enkle steg.,,Finn ditt neste kontor eller coworking space. Enkelt søk for din bedrift.,,,,https://spacefinder.no/
```

### Key Patterns from Spacefinder

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `{KeyWord:fallback}` | `{KeyWord:Kontor til leie i Bergen}` | ALWAYS in Headline 1 |
| `{LOCATION(City):fallback}` | `i {LOCATION(City):din by}` | National campaigns with geo targeting |
| Pin to position 1 | `Headline 1 position: 1` | ALWAYS for H1 |
| Pin to position 2 | `Headline 2 position: 2` | For brand campaigns or when H2 is critical |
| Multiple pins to same position | `Headline 3 position: 2, Headline 4 position: 2` | Brand campaigns - gives Google options for position 2 |
| Blank position | `Headline 5 position:` (empty) | Let Google rotate freely |

### Column Order for Google Ads Editor Import

```
Campaign, Ad Group, Headline 1, Headline 1 position, Headline 2, Headline 2 position, ... Headline 15, Headline 15 position, Description 1, Description 1 position, ... Description 4, Description 4 position, Path 1, Path 2, Final URL
```

---

---

## Tab 4: ROI Beregner (Calculator) - v3 COMPLETE SPECIFICATION

**CRITICAL**: This tab MUST be created using `scripts/add_roi_tab.py` to ensure consistent formatting.
If you cannot run the script, follow this EXACT specification.

### Quick Method (PREFERRED)
```bash
python scripts/add_roi_tab.py <spreadsheet_id> --client-name "Client Name"
```

### Manual Implementation (Only if script unavailable)

If you must create the ROI tab manually, follow this **EXACT** specification:

---

#### STEP 1: Row-by-Row Data Structure

| Row | Column A | Column B | Column C | Column D |
|-----|----------|----------|----------|----------|
| 1 | `ROI Beregner - {Client Name}` | (empty) | (empty) | (empty) |
| 2 | `Beregn forventet afkast af dine Google Ads` | (empty) | (empty) | (empty) |
| 3 | (empty) | (empty) | (empty) | (empty) |
| 4 | `📊 DINE TAL` | `Værdi` | `Hvad betyder det?` | (empty) |
| 5 | `Månedligt annoncebudget` | `{budget}` | `Hvor meget vil du bruge på Google Ads?` | (empty) |
| 6 | `Fortjeneste pr. kunde` | `{profit_per_customer}` | `Hvad tjener du på én kunde?` | (empty) |
| 7 | `Lukningsrate %` | `15` | `Hvor mange % af dine henvendelser bliver til salg?` | (empty) |
| 8 | (empty) | (empty) | (empty) | (empty) |
| 9 | `📈 KAMPAGNE ESTIMATER` | `Værdi` | `Hvad betyder det?` | (empty) |
| 10 | `Pris pr. klik (CPC)` | `{cpc}` | `Hvad koster ét klik på din annonce?` | (empty) |
| 11 | `Website konverteringsrate %` | `3` | `Hvor mange % af besøgende udfylder formularen?` | (empty) |
| 12 | (empty) | (empty) | (empty) | (empty) |
| 13 | `🧮 BEREGNEDE RESULTATER` | `Værdi` | `Forklaring` | `Beregning` |
| 14 | `Estimerede klik/måned` | `=ROUND(B5/B10,0)` | `Hvor mange klik kan du købe for dit budget?` | `=B5&" kr ÷ "&B10&" kr pr. klik = "&B14&" klik"` |
| 15 | `Estimerede leads/måned` | `=ROUND(B14*(B11/100),1)` | `Hvor mange udfylder kontaktformularen?` | `=B14&" klik × "&B11&"% = "&B15&" leads"` |
| 16 | `Estimerede kunder/måned` | `=ROUND(B15*(B7/100),1)` | `Hvor mange leads bliver til betalende kunder?` | `=B15&" leads × "&B7&"% = "&B16&" kunder"` |
| 17 | `Estimeret omsætning/måned` | `=ROUND(B16*B6,0)` | `Hvad tjener du på disse kunder?` | `=B16&" kunder × "&B6&" kr = "&B17&" kr"` |
| 18 | `Estimeret profit/måned` | `=B17-B5` | `Din fortjeneste efter annonceudgifter` | `=B17&" kr − "&B5&" kr = "&B18&" kr"` |
| 19 | `ROAS (Return on Ad Spend)` | `=ROUND(B17/B5,2)&"x"` | `For hver 1 kr brugt, får du X kr tilbage` | `=B17&" kr ÷ "&B5&" kr = "&ROUND(B17/B5,2)&"x"` |
| 20 | (empty) | (empty) | (empty) | (empty) |
| 21 | `STATUS` | `=IF(B18>0,"✅ Profitable","❌ Ikke profitable")` | `=IF(B18>0,"Du tjener penge på Google Ads! 🎉","Du taber penge - juster dine tal")` | (empty) |

---

#### STEP 2: Formatting Specification (REQUIRED)

**Row 1 - Title:**
- Font: Bold, 16pt
- Spans columns A-D visually

**Row 2 - Subtitle:**
- Font: Italic, gray text (`rgb(102,102,102)`)

**Row 4 - Section Header "📊 DINE TAL":**
- Background: Blue `rgb(64,115,179)` or `{"red":0.25,"green":0.45,"blue":0.7}`
- Text: Bold, White

**Row 9 - Section Header "📈 KAMPAGNE ESTIMATER":**
- Background: Teal `rgb(51,128,128)` or `{"red":0.2,"green":0.5,"blue":0.5}`
- Text: Bold, White

**Row 13 - Section Header "🧮 BEREGNEDE RESULTATER":**
- Background: Green `rgb(51,140,89)` or `{"red":0.2,"green":0.55,"blue":0.35}`
- Text: Bold, White

**Input Cells (B5:B7, B10:B11) - Yellow:**
- Background: Light yellow `rgb(255,242,204)` or `{"red":1.0,"green":0.95,"blue":0.8}`
- Text: Bold

**Calculated Results (B14:B19) - Light Green:**
- Background: Light green `rgb(217,242,217)` or `{"red":0.85,"green":0.95,"blue":0.85}`
- Text: Bold

**Explanation Column (C5:C7, C10:C11):**
- Text: Italic, Gray `rgb(102,102,102)`

**Calculation Column (D14:D19):**
- Background: Light gray `rgb(242,242,242)` or `{"red":0.95,"green":0.95,"blue":0.95}`
- Font: Monospace (Roboto Mono), 9pt

**Profit Cell (B18) - Conditional Formatting:**
- If > 0: Bright green background `rgb(179,230,179)` or `{"red":0.7,"green":0.9,"blue":0.7}`
- If ≤ 0: Light red background `rgb(242,179,179)` or `{"red":0.95,"green":0.7,"blue":0.7}`

---

#### STEP 3: Column Widths (REQUIRED)

| Column | Width (pixels) |
|--------|---------------|
| A | 250 |
| B | 120 |
| C | 320 |
| D | 280 |

---

#### STEP 4: Default Values

| Field | Default Value | Format |
|-------|---------------|--------|
| Lukningsrate % | 15 | Whole number (15 = 15%) |
| Website konverteringsrate % | 3 | Whole number (3 = 3%) |
| CPC | From keyword analysis, or 8 | DKK |

**ROAS Format**: Always shown as factor with "x" suffix (e.g., `2.94x` NOT `294%`)

---

#### STEP 5: Google Sheets API Implementation (for programmatic creation)

If creating via API, use these batchUpdate requests:

```python
# Section headers color values:
BLUE_HEADER = {"red": 0.25, "green": 0.45, "blue": 0.7}
TEAL_HEADER = {"red": 0.2, "green": 0.5, "blue": 0.5}
GREEN_HEADER = {"red": 0.2, "green": 0.55, "blue": 0.35}

# Cell background colors:
YELLOW_INPUT = {"red": 1.0, "green": 0.95, "blue": 0.8}
GREEN_OUTPUT = {"red": 0.85, "green": 0.95, "blue": 0.85}
GRAY_CALC = {"red": 0.95, "green": 0.95, "blue": 0.95}

# Conditional formatting colors:
PROFIT_POSITIVE = {"red": 0.7, "green": 0.9, "blue": 0.7}
PROFIT_NEGATIVE = {"red": 0.95, "green": 0.7, "blue": 0.7}

# Row indices (0-based):
TITLE_ROW = 0
SUBTITLE_ROW = 1
DINE_TAL_HEADER = 3
DINE_TAL_DATA = [4, 5, 6]  # B5:B7
KAMPAGNE_HEADER = 8
KAMPAGNE_DATA = [9, 10]    # B10:B11
RESULTATER_HEADER = 12
RESULTATER_DATA = [13, 14, 15, 16, 17, 18]  # B14:B19
STATUS_ROW = 20
```

---

### Visual Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ROI Beregner - Client Name                                                  │
│ Beregn forventet afkast af dine Google Ads                                  │
│                                                                             │
│ ████████████████████████████████████████████████████████████████████████████│
│ │ 📊 DINE TAL         │ Værdi │ Hvad betyder det?                │         │ ← BLUE
│ ├─────────────────────┼───────┼──────────────────────────────────┼─────────┤
│ │ Månedligt budget    │▓3500▓│ Hvor meget vil du bruge...?      │         │ ← Yellow
│ │ Fortjeneste/kunde   │▓1000▓│ Hvad tjener du på én kunde?      │         │ ← Yellow
│ │ Lukningsrate %      │▓ 65 ▓│ Hvor mange % bliver til salg?    │         │ ← Yellow
│ │                     │       │                                  │         │
│ ████████████████████████████████████████████████████████████████████████████│
│ │ 📈 KAMPAGNE EST.    │ Værdi │ Hvad betyder det?                │         │ ← TEAL
│ ├─────────────────────┼───────┼──────────────────────────────────┼─────────┤
│ │ Pris pr. klik (CPC) │▓ 11 ▓│ Hvad koster ét klik?             │         │ ← Yellow
│ │ Website conv. %     │▓  5 ▓│ % besøgende der udfylder form.   │         │ ← Yellow
│ │                     │       │                                  │         │
│ ████████████████████████████████████████████████████████████████████████████│
│ │ 🧮 BEREGNEDE RES.   │ Værdi │ Forklaring                       │Beregning│ ← GREEN
│ ├─────────────────────┼───────┼──────────────────────────────────┼─────────┤
│ │ Est. klik/måned     │░ 318 ░│ Hvor mange klik for dit budget?  │░formula░│ ← Lt Green
│ │ Est. leads/måned    │░15.9 ░│ Hvor mange udfylder form.?       │░formula░│ ← Lt Green
│ │ Est. kunder/måned   │░10.3 ░│ Hvor mange leads→kunder?         │░formula░│ ← Lt Green
│ │ Est. omsætning      │░10300░│ Hvad tjener du på kunderne?      │░formula░│ ← Lt Green
│ │ Est. profit         │░6800 ░│ Fortjeneste efter annonce        │░formula░│ ← Conditional!
│ │ ROAS                │░2.94x░│ For hver 1 kr → X kr tilbage     │░formula░│ ← Lt Green
│ │                     │       │                                  │         │
│ │ STATUS              │✅ Prof│ Du tjener penge på Google Ads! 🎉│         │
│ └─────────────────────┴───────┴──────────────────────────────────┴─────────┘
│
│ Legend: ▓▓▓ = Yellow input cells    ░░░ = Light green output cells
```

---

## Validation

Use `get_deliverable_schema("ad_copy")` from the MCP to fetch the schema and validate your output before delivery.
Use `get_deliverable_schema("roi_calculator")` for the ROI calculator tab.
