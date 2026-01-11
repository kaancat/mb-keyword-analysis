# Phase 3: Keyword Research Reference

Detailed guide for budget-aware, buyer-journey-based keyword research.

---

## Budget-First Approach (NEW)

**BEFORE any research, calculate maximum keyword count.**

See `decision-trees/budget-tiers.md` for full details.

### Quick Calculation

```
Daily budget = Monthly budget ÷ 30
Expected CPC = Industry average (check below)
Max daily clicks = Daily budget ÷ Expected CPC
Max keywords ≈ Max daily clicks × 2
```

### Budget Tier Implications

| Tier | Monthly Budget | Max Keywords | Match Type Bias |
|------|----------------|--------------|-----------------|
| Micro | <3,000 DKK | 30-50 | 80% Exact, 20% Phrase |
| Lean | 3,000-10,000 DKK | 50-100 | 60% Phrase, 40% Exact |
| Growth | 10,000-30,000 DKK | 100-200 | 50% Phrase, 30% Exact, 20% Broad |
| Scale | >30,000 DKK | 200+ | 40% Phrase, 30% Broad, 30% Exact |

### Industry CPC Reference (DKK)

| Industry | Low | Average | High |
|----------|-----|---------|------|
| Local Service (moving, cleaning) | 15 | 35 | 60 |
| E-commerce | 3 | 12 | 30 |
| B2B Services | 40 | 80 | 150 |
| SaaS | 25 | 55 | 100 |
| Legal/Finance | 80 | 150 | 300 |

---

## Positioning-First Research Strategy (CRITICAL)

**The biggest mistake:** Starting with generic commodity terms that any competitor would target.

**The fix:** Research positioning keywords FIRST, then expand outward.

### Pass 0: Positioning Keywords (MANDATORY)

**Before ANY generic research, use the `$POSITIONING_KEYWORDS` from Phase 1.**

```python
from backend.services.keyword_planner import KeywordPlannerService

kp = KeywordPlannerService()

# Example: Monday Brew positioning keywords
positioning_keywords = [
    # Problem keywords from positioning
    "marketing uden struktur",
    "uforudsigelig kundetilgang",
    "op og ned med kunder",
    "ingen faste leads",
    # Outcome keywords from positioning
    "forudsigelig leadgenerering",
    "stabil kundetilgang",
    "fyldt kalender",
    # Differentiation keywords
    "systembaseret marketing",
    "marketing system"
]

results = kp.generate_keyword_ideas(
    keywords=positioning_keywords,
    location_ids=[2208],
    language_id="1009"
)
```

**Expected outcome:**
- Many positioning keywords will have LOW or ZERO volume
- That's OK! The goal is to find RELATED terms that DO have volume
- Tag keywords from this pass with `Positioning: true`

**Why this matters:**
- "google ads bureau" = commodity (everyone targets this)
- "forudsigelig leadgenerering" = positioning (reflects unique value)
- Even if volume is lower, these keywords attract the RIGHT customers

---

## Buyer Journey Research Strategy

**AFTER Pass 0, research by buyer journey stage.**

### The Six Passes (1-6)

#### Pass 1: URL Seed
Let Google understand the business from the website.

```python
from backend.services.keyword_planner import KeywordPlannerService

kp = KeywordPlannerService()

results = kp.generate_keyword_ideas(
    page_url="https://client-website.dk",
    location_ids=[2208],  # Denmark
    language_id="1009"    # Danish
)
```

**Extract themes** → Group by topic for Pass 2.

#### Pass 2: Solution Keywords (High-Intent Core)
The most important pass. What are they looking for?

```python
# Theme: Google Ads
results = kp.generate_keyword_ideas(
    keywords=["google ads bureau", "google ads specialist", "google ads hjælp"],
    location_ids=[2208],
    language_id="1009"
)
```

#### Pass 3: Problem Keywords (Mid-Funnel Discovery)
What pain does customer have?

```python
# Problem keywords
results = kp.generate_keyword_ideas(
    keywords=["mine annoncer virker ikke", "ingen leads", "for dyrt per kunde"],
    location_ids=[2208],
    language_id="1009"
)
```

#### Pass 4: Proof Keywords (Consideration)
How do they validate?

```python
# Proof keywords
results = kp.generate_keyword_ideas(
    keywords=["google ads bureau anmeldelser", "bedste google ads", "google ads case"],
    location_ids=[2208],
    language_id="1009"
)
```

#### Pass 5: Action Keywords (Conversion)
How do they convert?

```python
# Action keywords
results = kp.generate_keyword_ideas(
    keywords=["book google ads møde", "få google ads tilbud", "google ads pris"],
    location_ids=[2208],
    language_id="1009"
)
```

#### Pass 6: Location × Service (For Local)
Only for geo-targeted businesses.

```python
# Location combinations
results = kp.generate_keyword_ideas(
    keywords=["google ads bureau københavn", "google ads aarhus"],
    location_ids=[2208],
    language_id="1009"
)
```

---

## Match Type Decision

See `decision-trees/match-type-strategy.md` for full decision flow.

### Quick Rules

| Keyword Type | Match Type | Reason |
|--------------|------------|--------|
| Brand | Exact | Protect brand traffic |
| Competitor | Exact | Control spend |
| High-intent action | Exact | Protect valuable clicks |
| Core service | Phrase | Allow modifiers |
| Problem/Discovery | Broad (if budget) or Phrase | Capture research |

### Budget-Based Mix

| Budget Tier | Exact | Phrase | Broad |
|-------------|-------|--------|-------|
| Micro | 80% | 20% | 0% |
| Lean | 40% | 60% | 0% |
| Growth | 30% | 50% | 20% |
| Scale | 30% | 40% | 30% |

### Match Type Rationale (Required)

Every keyword MUST have documented rationale:

```json
{
  "Keyword": "google ads bureau",
  "Match Type": "Phrase",
  "Match Type Rationale": "Core service term, good volume (880), Lean budget - default to Phrase"
}
```

---

## Negative Keywords

See `decision-trees/negative-keywords.md` for full framework.

### Three-Layer Structure

**Layer 1: Global Cross-Industry**
```
gratis, billig, DIY, selv, definition, pdf, job, karriere, løn,
wikipedia, youtube, reddit, hvad er
```

**Layer 2: Vertical-Specific**
Based on business type from Phase 1.

**Layer 3: Brand/Competitor Control**
- Block brand in non-brand campaigns
- Block competitors in brand campaigns

### Output: `negative_keywords.json`

```json
{
  "global": ["gratis", "billig", "DIY", "selv", "pdf", "job"],
  "vertical": ["praktik", "uddannelse", "kursus"],
  "brand_exclusions": ["competitor_name"],
  "campaign_specific": {
    "mb | DA | Search | Google Ads": ["facebook", "instagram"]
  }
}
```

---

## Service Verification (CRITICAL - Phase 3.5)

**The mondaybrew mistake:** LinkedIn keywords were included because URL-based research returned them, but mondaybrew doesn't offer LinkedIn services.

**The fix:** Validate EVERY keyword against `$CANONICAL_SERVICES` before finalizing.

### Keyword-Service Mapping

For each keyword, determine which canonical service it belongs to:

```python
def match_keyword_to_service(keyword, canonical_services):
    """
    Returns Service_ID if keyword matches a canonical service.
    Returns None if keyword doesn't match any service.
    """
    # Example matching logic:
    keyword_lower = keyword.lower()

    for service in canonical_services:
        for variation in service['variations']:
            if variation.lower() in keyword_lower:
                return service['id']

    return None  # No match - FLAG FOR REVIEW
```

### Validation Rules

| Keyword Contains | Maps To | Example |
|------------------|---------|---------|
| "google ads", "adwords", "google annoncering" | Google Ads (SVC-001) | "google ads bureau" → SVC-001 |
| "facebook", "instagram", "meta" | Meta Ads (SVC-002) | "facebook annoncering" → SVC-002 |
| "linkedin" | LinkedIn Ads | "linkedin marketing" → NO MATCH if not in Q9 |
| "tiktok" | TikTok Ads | "tiktok bureau" → NO MATCH if not in Q9 |
| "ecommerce", "webshop" | E-commerce | "ecommerce marketing" → NO MATCH if B2B only |

### Required Output Fields

Add these fields to EVERY keyword in `keyword_analysis.json`:

```json
{
  "Keyword": "annoncering på linkedin",
  "Service_ID": null,
  "Service_Validation": "UNMATCHED",
  "Include": false,
  "Exclusion_Reason": "LinkedIn not in $CANONICAL_SERVICES"
}
```

```json
{
  "Keyword": "google ads bureau",
  "Service_ID": "SVC-001",
  "Service_Validation": "MATCHED",
  "Include": true,
  "Exclusion_Reason": null
}
```

### Flagging Unmatched Keywords

For ANY keyword where `Service_ID = null`:

1. **Auto-exclude** if keyword clearly matches `$SERVICES_NOT_OFFERED`
2. **Flag for review** if uncertain
3. **Present to user** in Phase 3.5 for confirmation

### Cross-Platform Confusion Rules

These are commonly confused but are SEPARATE services:

| Often Confused | Actually Means |
|----------------|----------------|
| "Meta Ads" | Facebook + Instagram ONLY |
| "Social media marketing" | Could be ANY platform - need clarification |
| "LinkedIn Ads" | LinkedIn ONLY (NOT part of Meta) |
| "Google Ads" | Google Search + Display + YouTube |

### Quality Gate

Before Phase 3.5:
- [ ] Every keyword has `Service_ID` assigned (or `null`)
- [ ] Unmatched keywords are documented
- [ ] Clear `Exclusion_Reason` for excluded keywords

---

## Stop Criteria

Stop iterating when ALL conditions are met:

### 1. Service Coverage Complete
- Every service from Phase 1 has keywords
- Primary services have more depth than secondary

### 2. Buyer Journey Coverage
- Problem keywords captured
- Solution keywords captured
- Proof keywords captured
- Action keywords captured

### 3. Location Coverage (For Geo)
- Main target area has location variants
- "Near me" and location-specific terms included

### 4. Budget Alignment
- Total keywords within budget tier max
- Not exceeding realistic daily click capacity

### 5. Quality Check
**Average volume per keyword should be >200**

If average is lower, you have long-tail bloat:
- Remove low-volume keywords (<50/month)
- Consolidate similar variations
- Focus on head terms

---

## Location & Language IDs

### Countries

| Country | Location ID |
|---------|-------------|
| Denmark | 2208 |
| Norway | 2578 |
| Sweden | 2752 |

### Cities (Denmark)

| City | Location ID |
|------|-------------|
| Copenhagen | 1020424 |
| Aarhus | 1011990 |
| Odense | 1011997 |
| Aalborg | 1011993 |

### Cities (Norway)

| City | Location ID |
|------|-------------|
| Oslo | 1010874 |
| Bergen | 1010813 |
| Trondheim | 1010888 |
| Stavanger | 1010883 |

### Languages

| Language | ID |
|----------|-----|
| Danish | 1009 |
| Norwegian | 1012 |
| Swedish | 1015 |
| English | 1000 |

---

## Keyword Tagging

### Required Tags

| Tag | Values | Purpose |
|-----|--------|---------|
| Category | Service bucket from Phase 2 | Campaign assignment |
| Intent | High / Medium / Low | Bid prioritization |
| Buyer Journey | Problem / Solution / Proof / Action | Ad copy alignment |
| Include | true / false | Filter out irrelevant |

### Intent Classification

| Intent | Description | Examples |
|--------|-------------|----------|
| **High** | Ready to buy/book | "få tilbud", "book møde" |
| **Medium** | Comparing options | "pris", "bedste" |
| **Low** | Research/info | "hvad er", "hvordan" |

---

## Output Format

### `keyword_analysis.json`

```json
[
  {
    "Keyword": "google ads bureau",
    "Avg. Monthly Searches": 880,
    "Competition": "High",
    "Top of page bid (low range)": "DKK 45.00",
    "Top of page bid (high range)": "DKK 120.00",
    "Category": "Google Ads",
    "Intent": "High",
    "Buyer Journey": "Solution",
    "Match Type": "Phrase",
    "Match Type Rationale": "Core service term, good volume, Lean budget tier",
    "Include": true
  }
]
```

### Currency Rules

**CRITICAL:** Format bids in target market currency.

| Target Market | Currency | Format |
|---------------|----------|--------|
| Denmark | DKK | "DKK 45.00" |
| Norway | NOK | "NOK 55.00" |
| Sweden | SEK | "SEK 48.00" |

**Never deliver USD values to Nordic clients.**

---

## Quality Gate Checklist

Before proceeding to Phase 3.5, verify:

- [ ] **Pass 0 (Positioning keywords) completed FIRST** (if `$POSITIONING_MODE = 'deep'`)
- [ ] **At least 10-20% of keywords tagged `Positioning: true`** (if `$POSITIONING_MODE = 'deep'`)
- [ ] Multiple research passes completed (Pass 0 + all 6)
- [ ] All services have keyword coverage
- [ ] Buyer journey stages covered (Problem, Solution, Proof, Action)
- [ ] Match types are varied with documented rationale
- [ ] Currency is correct for target market
- [ ] Total keywords within budget tier max
- [ ] Average volume per keyword >200 (no long-tail bloat)
- [ ] Negative keyword lists generated (3 layers)
- [ ] Category, Intent, Buyer Journey tags applied
- [ ] **`Service_ID` assigned to every keyword**
- [ ] **Unmatched keywords flagged for Phase 3.5 review**

**If positioning keywords are missing (and required): STOP. Go back to Pass 0.**
**If Service_ID is missing: STOP. Complete service mapping before Phase 3.5.**

---

## Common Mistakes

1. **Single-pass research** - Only running URL seed once
2. **Ignoring buyer journey** - All keywords are Solution stage
3. **Budget blindness** - 500 keywords for 5K DKK budget
4. **All Phrase match** - No differentiation by intent/volume
5. **Wrong currency** - USD instead of DKK
6. **Missing misspellings** - "brudkjole" has 8,100 searches
7. **Long-tail bloat** - Avg volume per keyword <100
8. **No negative lists** - Missing Layer 1/2/3 negatives
9. **No rationale** - Match types without explanation
