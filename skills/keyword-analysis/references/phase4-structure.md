# Phase 4: Campaign Structure Reference

Detailed guide for campaign architecture, split/consolidate decisions, and naming conventions.

---

## Prerequisites

Phase 3 must be complete with:
- `keyword_analysis.json` - All keywords with tags
- `negative_keywords.json` - Three-layer negative lists
- Match types assigned with rationale
- Budget tier confirmed

---

## Split vs Consolidate Framework

See `decision-trees/campaign-split-logic.md` for detailed rules.

### Always Split (Non-Negotiable)

| Split Type | Reason |
|------------|--------|
| Brand vs Non-Brand | Different intent, CPC, conversion rates |
| B2B vs B2C | Different buyer journeys, landing pages |
| Search vs Shopping vs PMax | Different networks, strategies |

### Data-Driven Splits

| Condition | Action |
|-----------|--------|
| Segment ≥25% of spend with ≥5 conv/month | Split |
| CVR differs ≥30% over ≥100 clicks | Split |
| Different landing pages required | Split |
| Customer value differs >30% | Split |

### Budget-Driven Consolidation

| Condition | Action |
|-----------|--------|
| Campaign <15 conversions/month expected | Consolidate |
| Ad groups <30 clicks each expected | Consolidate |
| Budget <100 DKK/day per campaign | Consolidate |

### Campaign Count by Budget

| Budget Tier | Max Campaigns | Structure |
|-------------|---------------|-----------|
| Micro (<3K) | 2 | Brand + 1 core |
| Lean (3K-10K) | 3-4 | Brand + 2-3 themes |
| Growth (10K-30K) | 4-6 | Full service |
| Scale (>30K) | 6+ | Service + Geo + Persona |

---

## Naming Conventions

### Campaign Names

**Format:** `mb | {LANG} | {Type} | {Theme}`

| Component | Options | Examples |
|-----------|---------|----------|
| mb | Always "mb" | mb |
| LANG | DA, NO, SE, EN | DA |
| Type | Search, Shopping, PMax, Brand | Search |
| Theme | Service/category | Google Ads, CRM |

**Examples:**
```
mb | DA | Search | Google Ads
mb | DA | Search | CRM
mb | DA | Brand | mondaybrew
mb | NO | Search | Kontorleie
mb | DA | PMax | Produkter
```

### Ad Group Names

**Format:** `{Theme} | {Location}`

If no location targeting: `{Theme} | General`

**Examples:**
```
Google Ads Bureau | Danmark
CRM Implementering | København
Kontorleie | Oslo
Kontorleie | Bergen
```

### Geographic Splits

When splitting by geography:
```
Campaign: mb | DA | Search | Flytning | København
Ad Group: Erhvervsflytning | København
Ad Group: Privatflytning | København

Campaign: mb | DA | Search | Flytning | Aarhus
Ad Group: Erhvervsflytning | Aarhus
Ad Group: Privatflytning | Aarhus
```

---

## Ad Group Structure

### Keywords Per Ad Group

| Tier | Keywords/Ad Group | Rationale |
|------|-------------------|-----------|
| Tight | 5-10 | Focused, easier to optimize |
| Standard | 10-15 | Good coverage, manageable |
| Avoid | >15 | Diluted relevance |

### Grouping Logic

1. **Group by theme** - All keywords about same topic
2. **Group by intent** - High-intent separate from research
3. **Group by landing page** - All keywords going to same URL

**Good grouping:**
```
Ad Group: Google Ads Bureau
- google ads bureau
- google ads specialist
- google ads hjælp
- professionel google ads
```

**Bad grouping:**
```
Ad Group: Marketing (too broad)
- google ads bureau
- facebook marketing
- email marketing
- seo hjælp
```

---

## Landing Page Assignment

### Rules

1. **Use specific pages** - Never homepage for everything
2. **Match theme to page** - Ad group theme = landing page content
3. **Flag missing pages** - If no page exists, note "needs landing page"

### Assignment Matrix

| Ad Group Theme | Landing Page | Fallback |
|----------------|--------------|----------|
| Google Ads | /google-ads/ | /services/ |
| CRM | /crm/ | /services/ |
| Websites | /websites/ | Homepage (flag) |

### Red Flags

**If >50% of keywords go to homepage:**
- Quality Score will suffer
- Discuss with user before proceeding
- Options: create pages, limit scope, accept lower QS

---

## Bid Strategy Recommendations

### By Campaign Type

| Campaign Type | Recommended Strategy | Alternative |
|---------------|---------------------|-------------|
| Brand | Target Impression Share (90%+) | Max Clicks |
| Non-Brand (new) | Maximize Conversions | Max Clicks |
| Non-Brand (data) | Target CPA | tROAS |
| Shopping | Maximize Conversion Value | tROAS |
| PMax | Maximize Conversions | Value-based |

### By Budget Tier

| Tier | Recommended | Rationale |
|------|-------------|-----------|
| Micro | Max Clicks → Manual CPC | Need control, limited data |
| Lean | Maximize Conversions | Let Google optimize |
| Growth | Target CPA | Enough data for targets |
| Scale | tROAS / Target CPA | Performance-based |

### Learning Period

- New campaigns need 2-4 weeks of data
- Don't change strategy during learning
- Minimum 15 conversions before Target CPA works

---

## Budget Allocation

### General Framework

| Campaign Type | Budget % | Rationale |
|---------------|----------|-----------|
| Brand | 10-20% | Protect, cheap clicks |
| Core Service | 40-50% | Main revenue driver |
| Secondary Service | 20-30% | Supporting revenue |
| Discovery/Competitor | 10-20% | Expansion |

### Example Allocation (10,000 DKK/month)

```
mb | DA | Brand | mondaybrew: 1,500 DKK (15%)
mb | DA | Search | Google Ads: 4,500 DKK (45%)
mb | DA | Search | CRM: 3,000 DKK (30%)
mb | DA | Search | Websites: 1,000 DKK (10%)
```

### Reallocation Triggers

Move budget when:
- Campaign exhausting budget daily → Increase
- Campaign underspending → Decrease or fix issues
- Strong performer emerging → Allocate more
- Poor performer identified → Reduce or pause

---

## Output Format

### `campaign_structure.json`

```json
[
  {
    "Campaign": "mb | DA | Search | Google Ads",
    "Ad Group": "Google Ads Bureau | Danmark",
    "Keyword": "google ads bureau",
    "Match Type": "Phrase",
    "Final URL": "https://mondaybrew.dk/google-ads/",
    "Split Rationale": "Core service, separate from CRM due to different customer journey"
  },
  {
    "Campaign": "mb | DA | Search | Google Ads",
    "Ad Group": "Google Ads Bureau | Danmark",
    "Keyword": "google ads specialist",
    "Match Type": "Phrase",
    "Final URL": "https://mondaybrew.dk/google-ads/",
    "Split Rationale": ""
  }
]
```

### `bid_strategy_recommendations.md`

```markdown
# Bid Strategy Recommendations: {Client Name}

## Overview

Budget Tier: Lean (7,000 DKK/month)
Conversion Tracking: Form submissions
Historical Data: None (new account)

## Campaign Strategies

### mb | DA | Brand | mondaybrew

**Strategy:** Target Impression Share
**Target:** 90% top of page
**Rationale:** Protect brand, cheap clicks, must own SERP
**Budget:** 1,000 DKK/month

### mb | DA | Search | Google Ads

**Strategy:** Maximize Conversions
**Rationale:** New campaign, need data before setting CPA targets
**Budget:** 3,500 DKK/month
**Review:** Switch to Target CPA after 15 conversions

### mb | DA | Search | CRM

**Strategy:** Maximize Conversions
**Rationale:** New campaign, secondary service
**Budget:** 2,500 DKK/month

## Budget Allocation

| Campaign | Monthly | Daily | % |
|----------|---------|-------|---|
| Brand | 1,000 DKK | 33 DKK | 14% |
| Google Ads | 3,500 DKK | 117 DKK | 50% |
| CRM | 2,500 DKK | 83 DKK | 36% |

## Optimization Triggers

1. After 15 conversions in Google Ads campaign → Switch to Target CPA
2. If CRM underspends consistently → Reallocate to Google Ads
3. If brand campaign sees competitor ads → Increase budget
```

---

## Quality Gate Checklist

Before proceeding to Phase 5, verify:

- [ ] All keywords assigned to ad groups
- [ ] Ad groups have 5-15 keywords each
- [ ] Campaign names follow `mb | LANG | Type | Theme`
- [ ] Ad group names follow `Theme | Location`
- [ ] Brand and non-brand are separate campaigns
- [ ] B2B and B2C are separate (if both exist)
- [ ] Landing pages are specific (not all homepage)
- [ ] Split/consolidate decisions documented with rationale
- [ ] Bid strategies recommended per campaign
- [ ] Budget allocation defined
- [ ] Campaign count within budget tier max

---

## Common Mistakes

1. **Too many campaigns for budget** - Budget fragmentation
2. **Brand + Non-Brand together** - Inflated metrics
3. **B2B + B2C together** - Poor targeting
4. **>15 keywords per ad group** - Diluted relevance
5. **All homepage URLs** - Low Quality Score
6. **No split rationale** - Can't explain decisions
7. **Wrong bid strategies** - Target CPA without data
8. **Uneven budget allocation** - Starving top performers
