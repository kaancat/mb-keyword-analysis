# Phase 6: ROI Projection Reference

Detailed guide for scenario-based ROI modeling and scaling projections.

---

## Prerequisites

Phase 5 must be complete with:
- `ad_copy.json` - All ads created
- `campaign_structure.json` - Campaign architecture
- `keyword_analysis.json` - Keywords with bid data
- Budget confirmed from Phase 1
- Customer value from user

---

## Three-Scenario Framework (NEW)

**Always provide three scenarios, not just one projection.**

### Scenario Definitions

| Scenario | Conversion Rate | Close Rate | When It Happens |
|----------|-----------------|------------|-----------------|
| **Conservative** | -30% from expected | -25% from expected | Poor landing pages, weak follow-up |
| **Expected** | Industry benchmark | Industry benchmark | Standard performance |
| **Optimistic** | +50% from expected | +25% from expected | Optimized funnel, strong sales |

### Industry Benchmarks

| Business Type | Conversion Rate | Close Rate |
|---------------|-----------------|------------|
| Local Service | 5-8% | 20-30% |
| E-commerce | 2-4% | N/A (direct) |
| B2B Service | 3-5% | 15-25% |
| SaaS | 4-7% | 10-20% |
| Agency | 3-5% | 15-20% |

---

## Calculation Formula

### Core Metrics

```
Monthly Clicks = Monthly Budget ÷ Average CPC
Monthly Leads = Monthly Clicks × Conversion Rate
Monthly Customers = Monthly Leads × Close Rate
Monthly Revenue = Monthly Customers × Customer Value
Monthly Profit = Monthly Revenue - Monthly Budget
ROAS = Monthly Revenue ÷ Monthly Budget
ROI = (Monthly Profit ÷ Monthly Budget) × 100
```

### Average CPC Calculation

From `keyword_analysis.json`:
```
Weighted Avg CPC = Σ(Keyword Volume × Keyword Avg Bid) ÷ Σ(Keyword Volume)
```

Or use mid-point:
```
Avg CPC = (Low Bid + High Bid) ÷ 2
```

---

## Scenario Calculations

### Example: B2B Service

**Inputs:**
- Budget: 5,000 DKK/month
- Average CPC: 90 DKK
- Customer Value: 50,000 DKK
- Expected Conversion Rate: 5%
- Expected Close Rate: 20%

### Conservative Scenario

```
Conversion Rate: 5% × 0.70 = 3.5%
Close Rate: 20% × 0.75 = 15%

Clicks: 5,000 ÷ 90 = 55
Leads: 55 × 3.5% = 1.9
Customers: 1.9 × 15% = 0.29
Revenue: 0.29 × 50,000 = 14,500 DKK
ROAS: 14,500 ÷ 5,000 = 2.9x
```

### Expected Scenario

```
Conversion Rate: 5%
Close Rate: 20%

Clicks: 5,000 ÷ 90 = 55
Leads: 55 × 5% = 2.75
Customers: 2.75 × 20% = 0.55
Revenue: 0.55 × 50,000 = 27,500 DKK
ROAS: 27,500 ÷ 5,000 = 5.5x
```

### Optimistic Scenario

```
Conversion Rate: 5% × 1.50 = 7.5%
Close Rate: 20% × 1.25 = 25%

Clicks: 5,000 ÷ 90 = 55
Leads: 55 × 7.5% = 4.13
Customers: 4.13 × 25% = 1.03
Revenue: 1.03 × 50,000 = 51,500 DKK
ROAS: 51,500 ÷ 5,000 = 10.3x
```

---

## Break-Even Analysis (NEW)

### Minimum Budget for Statistical Significance

**Formula:**
```
Min Budget = Required Clicks × Average CPC
Required Clicks = 100 (per variant, for optimization)
```

**Example:**
```
Average CPC: 90 DKK
Required Clicks: 100
Min Budget: 100 × 90 = 9,000 DKK (for one test)
```

### Minimum Budget for Conversions

**Formula:**
```
Min Budget = Target Conversions × CPC ÷ Conversion Rate
```

**Example:**
```
Target: 5 conversions/month (minimum for optimization)
CPC: 90 DKK
Conversion Rate: 5%

Min Clicks: 5 ÷ 0.05 = 100 clicks
Min Budget: 100 × 90 = 9,000 DKK/month
```

### Break-Even Customer Value

**Formula:**
```
Break-Even Value = Monthly Budget ÷ Expected Customers
```

**Example:**
```
Budget: 5,000 DKK
Expected Customers: 0.55

Break-Even Value: 5,000 ÷ 0.55 = 9,091 DKK per customer
```

If customer value > break-even value, campaign is profitable.

---

## Scaling Projections (NEW)

### 2x Budget Projection

**Not linear scaling.** At higher budgets:
- CPC may increase (auction dynamics)
- Conversion rate may decrease (lower-quality traffic)
- But total volume increases

**Conservative 2x Model:**
```
Budget: 10,000 DKK (2x)
CPC: 95 DKK (+5% due to increased competition)
Conversion Rate: 4.5% (-10% as reaching more cold traffic)
```

### 3x Budget Projection

```
Budget: 15,000 DKK (3x)
CPC: 100 DKK (+11%)
Conversion Rate: 4% (-20%)
```

### Scaling Milestones

| Budget Level | Next Action |
|--------------|-------------|
| Current | Optimize existing campaigns |
| 2x | Add secondary services, expand geo |
| 3x | Add competitor campaign, full funnel |
| 5x | Persona-based campaigns, PMax |

---

## Output Format

### `roi_calculator.json`

```json
{
  "budget": 5000,
  "currency": "DKK",
  "cpc": 90.44,
  "estimated_clicks": 55,
  "conversion_rate": 0.05,
  "estimated_leads": 2.75,
  "close_rate": 0.20,
  "estimated_customers": 0.55,
  "profit_per_customer": 50000,
  "estimated_revenue": 27500,
  "roas": 5.5,
  "notes": {
    "assumptions": [
      "CPC based on weighted average of keyword bid estimates",
      "Conversion rate of 5% typical for B2B service landing pages",
      "Close rate of 20% assumes proper follow-up and qualification",
      "Customer value of 50,000 DKK assumes annual retainer model"
    ],
    "scenarios": {
      "conservative": {
        "conversion_rate": 0.035,
        "close_rate": 0.15,
        "estimated_customers": 0.29,
        "estimated_revenue": 14500,
        "roas": 2.9
      },
      "optimistic": {
        "conversion_rate": 0.075,
        "close_rate": 0.25,
        "estimated_customers": 1.03,
        "estimated_revenue": 51500,
        "roas": 10.3
      }
    },
    "break_even": {
      "min_customer_value": 9091,
      "current_customer_value": 50000,
      "profitable": true
    }
  }
}
```

### `scaling_roadmap.md` (NEW)

```markdown
# Scaling Roadmap: {Client Name}

## Current State

| Metric | Value |
|--------|-------|
| Monthly Budget | 5,000 DKK |
| Expected ROAS | 5.5x |
| Expected Customers | 0.55/month |

## Break-Even Analysis

- **Minimum customer value for profitability:** 9,091 DKK
- **Actual customer value:** 50,000 DKK
- **Margin above break-even:** 5.5x

## Scaling Projections

### Phase 1: Current (5,000 DKK/month)

**Focus:** Optimize existing campaigns
**Actions:**
- Run campaigns for 30 days
- Identify top-performing ad groups
- Build conversion data for Smart Bidding

**Success Criteria:**
- 3+ conversions/month
- CVR > 3%

### Phase 2: Growth (10,000 DKK/month)

**When to Scale:** After 15 conversions total
**Focus:** Expand coverage

**Actions:**
- Add secondary service campaigns
- Expand geographic targeting
- Implement Target CPA bidding

**Expected Results:**
| Metric | Current | At 2x Budget |
|--------|---------|--------------|
| Budget | 5,000 | 10,000 |
| Clicks | 55 | 105 |
| Leads | 2.75 | 4.73 |
| Customers | 0.55 | 0.85 |
| ROAS | 5.5x | 4.3x |

Note: ROAS decreases as we expand to less proven terms.

### Phase 3: Scale (20,000 DKK/month)

**When to Scale:** After 50 conversions and consistent CVR
**Focus:** Full funnel coverage

**Actions:**
- Add competitor campaign
- Launch PMax for brand awareness
- Persona-based campaign split

**Expected Results:**
| Metric | Phase 2 | At 4x Budget |
|--------|---------|--------------|
| Budget | 10,000 | 20,000 |
| Clicks | 105 | 200 |
| Leads | 4.73 | 8.00 |
| Customers | 0.85 | 1.44 |
| ROAS | 4.3x | 3.6x |

## Optimization Milestones

| Milestone | Trigger | Action |
|-----------|---------|--------|
| 15 conversions | Data threshold | Enable Target CPA |
| CVR < 3% | Performance issue | Audit landing pages |
| ROAS > 8x | Opportunity | Increase budget |
| ROAS < 2x | Risk | Pause underperformers |

## Long-Term Potential

At optimal scale (assuming market size):
- **Addressable monthly search volume:** [X] searches
- **Maximum profitable budget:** [X] DKK/month
- **Ceiling ROAS:** [X]x (diminishing returns)
```

---

## Quality Gate Checklist

Before proceeding to Phase 7, verify:

- [ ] Three scenarios calculated (conservative, expected, optimistic)
- [ ] ROAS calculated for each scenario
- [ ] Assumptions documented and reasonable
- [ ] Break-even analysis completed
- [ ] Customer value confirmed with user
- [ ] Scaling roadmap created with milestones
- [ ] Currency is correct for target market

---

## Common Mistakes

1. **Single scenario only** - No range of outcomes
2. **Unrealistic conversion rates** - Using 10% for B2B (too high)
3. **Ignoring close rate** - Leads ≠ customers
4. **Linear scaling assumptions** - 2x budget ≠ 2x results
5. **No break-even analysis** - Don't know minimum viable customer value
6. **Missing assumptions** - Can't explain the numbers
7. **Wrong currency** - USD instead of DKK
8. **No optimization milestones** - Don't know when to adjust
