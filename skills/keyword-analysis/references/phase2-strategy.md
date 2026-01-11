# Phase 2: Strategic Analysis Reference

Detailed guide for competitive analysis, buyer personas, and campaign planning.

---

## Prerequisites

Phase 1 must be complete with:
- `website_content.md` - Business understanding
- `landing_page_audit.md` - Available landing pages
- Business type detected
- Budget tier identified
- Buyer journey keywords mapped

---

## Buyer Personas

**Define 2-3 distinct searcher types before keyword research.**

### Three Standard Personas

| Persona | Mindset | Search Behavior | Conversion Path |
|---------|---------|-----------------|-----------------|
| **High-Intent** | "I need this now" | Specific terms, action words | Direct to contact |
| **Research** | "Which option is best?" | Comparison, reviews, features | Multiple touchpoints |
| **Problem-Aware** | "I have a problem but don't know the solution" | Questions, symptoms, pain points | Education → nurture |

### Persona Template

For each persona, document:

```markdown
## Persona 1: High-Intent Buyer

**Profile:**
- Knows what they need
- Ready to make contact
- Comparing 2-3 options

**Search Behavior:**
- "google ads bureau"
- "book google ads konsultation"
- "google ads tilbud"

**Conversion Path:**
Homepage → Service page → Contact form

**Ad Copy Angle:**
- Urgency ("Book i dag")
- Proof ("100+ kunder")
- Easy action ("Gratis samtale")
```

### Persona Mapping by Business Type

| Business Type | Primary Persona | Secondary Persona |
|---------------|-----------------|-------------------|
| Local Service | High-Intent | Problem-Aware |
| E-commerce | High-Intent | Research |
| Lead Gen (B2B) | Research | Problem-Aware |
| SaaS | Research | Problem-Aware |
| Agency | Research | High-Intent |

---

## Competitive Analysis

### What to Analyze

1. **Who's bidding on these terms?**
   - Run searches in target market
   - Note ad copy themes
   - Check landing page approaches

2. **What's their positioning?**
   - How do competitors describe themselves?
   - What USPs do they emphasize?
   - What's missing that client can claim?

3. **Auction Insights** (if existing account)
   - Impression share
   - Average position
   - Overlap rate with competitors

### Competitive Positioning Map

```
                    High Price
                        │
                        │
           Premium      │      Enterprise
           Boutique     │      Full-Service
                        │
    ────────────────────┼────────────────────
                        │
           Budget       │      Mid-Market
           Self-Serve   │      Balanced
                        │
                    Low Price

                    Low ──────────── High
                       Service Level
```

Plot client and competitors on this map.

### Output in `potential_analysis.md`

```markdown
## Competitive Landscape

### Key Competitors
1. **Competitor A** - [Positioning], [Strengths], [Weaknesses]
2. **Competitor B** - [Positioning], [Strengths], [Weaknesses]

### Client Positioning
- **Differentiation:** [What makes client unique]
- **Opportunity:** [Gap in market client can fill]

### Competitive Keyword Strategy
- **Direct competition:** [Keywords where we'll compete head-on]
- **Blue ocean:** [Keywords competitors aren't targeting]
- **Competitor targeting:** [Whether to target competitor brand terms]
```

---

## Keyword Opportunity Matrix

**Prioritize keywords by Volume × Intent × Competition**

### The Matrix

| Quadrant | Volume | Intent | Competition | Priority |
|----------|--------|--------|-------------|----------|
| **Gold** | High | High | Any | 1 (must have) |
| **Silver** | Medium | High | Low-Med | 2 (high value) |
| **Bronze** | Low | High | Low | 3 (precision targeting) |
| **Discovery** | High | Low | Low | 4 (budget permitting) |
| **Avoid** | Low | Low | High | Skip |

### Budget-Adjusted Priority

| Budget Tier | Focus Quadrants |
|-------------|-----------------|
| Micro (<3K) | Gold only |
| Lean (3K-10K) | Gold + Silver |
| Growth (10K-30K) | Gold + Silver + Bronze |
| Scale (>30K) | All including Discovery |

---

## Campaign Segmentation Rationale

### When to Create Separate Campaigns

See `decision-trees/campaign-split-logic.md` for detailed rules.

**Always Separate:**
- Brand vs Non-Brand
- B2B vs B2C
- Search vs Shopping vs PMax

**Data-Driven Splits:**
- ≥25% of spend with ≥5 conversions → Split
- CVR differs ≥30% over 100 clicks → Split
- Different landing pages → Split
- Different customer values (>30%) → Split

**Don't Split When:**
- <15 conversions/month per campaign
- <100 DKK/day per campaign
- <30 clicks per ad group

### Campaign Count by Budget

| Budget | Max Campaigns | Structure |
|--------|---------------|-----------|
| Micro | 2 | Brand + 1 core theme |
| Lean | 3-4 | Brand + 2-3 themes |
| Growth | 4-6 | Full service coverage |
| Scale | 6+ | Service + Geo + Persona |

---

## Ad Copy Strategy

### Strategy by Persona

| Persona | Headline Focus | Description Focus | CTA Type |
|---------|---------------|-------------------|----------|
| High-Intent | {KeyWord} + Urgency | Process + Speed | "Book nu" |
| Research | Category + Differentiator | Why us + Trust | "Få tilbud" |
| Problem-Aware | Pain point + Solution | Outcomes + Easy start | "Se hvordan" |

### USP to Ad Copy Mapping

For each USP from Phase 1:
1. Create benefit headline (what they get)
2. Create proof headline (why to believe)

**Example:**
```
USP: "Vi bygger systemer, ikke kampagner"

Benefit headline: "Få et system der virker"
Proof headline: "System-baseret tilgang"
```

### CTA Alignment

| Conversion Goal | CTAs to Use |
|-----------------|-------------|
| Form fills | "Få tilbud", "Book samtale", "Kontakt os" |
| Phone calls | "Ring nu", "Tal med os i dag" |
| Purchases | "Køb nu", "Bestil i dag" |
| Demos | "Se demo", "Prøv gratis" |
| Downloads | "Download guide", "Få vores tips" |

---

## ROI Projection (Preliminary)

**Rough estimate before keyword data.**

### Formula

```
Estimated monthly clicks = Budget ÷ Estimated CPC
Estimated leads = Clicks × Conversion Rate (3-5%)
Estimated customers = Leads × Close Rate (15-25%)
Estimated revenue = Customers × Customer Value
ROAS = Revenue ÷ Budget
```

### Industry Benchmarks

| Industry | Avg CPC (DKK) | Conversion Rate | Close Rate |
|----------|---------------|-----------------|------------|
| Local Service | 20-40 | 5-8% | 20-30% |
| E-commerce | 5-15 | 2-4% | N/A (direct sale) |
| B2B Service | 50-150 | 3-5% | 15-25% |
| SaaS | 30-80 | 4-7% | 10-20% |

---

## Output: `potential_analysis.md`

```markdown
# Potentialeanalyse: {Client Name}

## 1. Executive Summary

[2-3 paragraphs: Opportunity, recommended approach, expected outcome]

## 2. Website & Service Audit

### Business Type: [Lead Gen B2B / Local Service / etc.]

### Services Analyzed:
- **{Service 1}**: [Landing page ready, high priority]
- **{Service 2}**: [Landing page ready, medium priority]

### Key Findings:
- [Finding 1]
- [Finding 2]

## 3. Competitive Landscape

### Key Competitors:
1. **{Competitor 1}**: [Positioning]
2. **{Competitor 2}**: [Positioning]

### Client Differentiation:
[What makes client unique in the market]

## 4. Keyword Opportunity Summary

### Expected Coverage:
- Total estimated keywords: [X based on budget tier]
- Services covered: [List]
- Geographic coverage: [National / City-specific]

### Keyword Categories:
1. {Category 1}: High-intent, [X] keywords expected
2. {Category 2}: Solution-focused, [X] keywords expected

## 5. Proposed Campaign Structure

### Campaigns:
| Campaign | Purpose | Budget Allocation |
|----------|---------|-------------------|
| mb | DA | Brand | {Name} | Protect brand | 15% |
| mb | DA | Search | {Theme 1} | Core service | 45% |
| mb | DA | Search | {Theme 2} | Secondary | 40% |

### Split/Consolidate Rationale:
[Why this structure makes sense for budget and goals]

## 6. Ad Copy Strategy

### Personas Targeted:
1. **High-Intent**: [Approach]
2. **Research**: [Approach]

### Key Messages:
- USP 1 → "Headline angle"
- USP 2 → "Headline angle"

## 7. ROI Projection (Preliminary)

| Metric | Conservative | Expected | Optimistic |
|--------|--------------|----------|------------|
| Monthly Budget | {X} DKK | {X} DKK | {X} DKK |
| Est. Clicks | {X} | {X} | {X} |
| Est. Leads | {X} | {X} | {X} |
| Est. Customers | {X} | {X} | {X} |
| ROAS | {X}x | {X}x | {X}x |

## 8. Next Steps

1. Proceed to keyword research (Phase 3)
2. [Any blockers or questions for user]
```

---

## Output: `buyer_personas.md`

```markdown
# Buyer Personas: {Client Name}

## Persona 1: High-Intent Buyer

**Description:** Decision-maker who knows what they need and is ready to act.

**Demographics:**
- Role: [e.g., Marketing Manager, CEO]
- Company size: [e.g., SMB 10-50 employees]
- Budget authority: Yes

**Search Behavior:**
- Keywords: "google ads bureau", "google ads specialist", "hire google ads"
- Time to convert: 1-2 sessions
- Touchpoints: Service page → Contact form

**Pain Points:**
- [Pain point 1]
- [Pain point 2]

**Ad Copy Angle:**
- H1: {KeyWord} variant
- H2: Urgency ("Book i dag")
- Descriptions: Process, speed, proof

---

## Persona 2: Research Buyer

**Description:** Comparing options, needs education and proof.

[Continue same format...]

---

## Persona 3: Problem-Aware

**Description:** Knows they have a problem, doesn't know the solution exists.

[Continue same format...]
```
