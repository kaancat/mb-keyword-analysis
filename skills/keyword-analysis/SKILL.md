---
name: Keyword Analysis Workflow
description: This skill should be used when the user asks to "do keyword research", "create a keyword analysis", "build a Google Ads campaign", "research keywords for", "create a deliverable", or mentions "Tab 1", "keyword analysis", "Google Ads", or provides a client website URL. Orchestrates the full Monday Brew workflow from website understanding to final presentation deliverable.
version: 3.0.0
---

# Keyword Analysis Workflow (Professional-Grade)

Complete Google Ads campaign planning workflow in **8 phases**. Each phase produces a clear artifact and **blocks** the next phase.

This skill transforms you from a checklist-follower into a **senior PPC specialist** who:
- **Interviews the client first** - Websites don't tell the whole story
- Understands the business model and buyer journey
- Makes budget-aware decisions (knows 5K DKK/month can't support 500 keywords)
- Uses match types strategically based on volume, budget, intent, and conversion thresholds
- Structures campaigns by **business value**, not just service categories
- Creates buyer-persona-specific ad copy
- Knows when to consolidate vs split campaigns
- **Queries the RAG knowledge base** when facing ambiguous decisions

---

## CRITICAL RULES

1. **Never skip Phase 0** - Discovery interview blocks everything else
2. **Every discovery question must drive a decision** - No info gathering for its own sake
3. **Query RAG at decision points** - Not decoration, but informed decision-making
4. **Never do single-pass research** - Phase 3 requires multiple API iterations
5. **Never default all keywords to Phrase match** - Read and apply match type rules from `decision-trees/match-type-strategy.md`
6. **Always use sentence case in ad copy** - Not Title Case
7. **Always use specific landing pages** - Never homepage for everything
8. **Currency must match target market** - DKK for Denmark, NOK for Norway, SEK for Sweden
9. **Budget determines keyword count** - Read and apply limits from `decision-trees/budget-tiers.md`
10. **Average volume per keyword should be >200** - If lower, you have long-tail bloat

---

## Phase Overview

| Phase | Output Artifact(s) | Gate | What It Determines |
|-------|-------------------|------|-------------------|
| **0. Discovery Interview** | `discovery_brief.md` | BLOCKS ALL | Budget tier, focus areas, max CPC, services to advertise |
| 1. Business Deep-Dive | `website_content.md` | BLOCKS Phase 2 | Canonical services, business type, landing pages |
| 2. Strategic Analysis | `potential_analysis.md` | BLOCKS Phase 3 | Personas, competitive gaps, campaign segmentation |
| 3. Keyword Research | `keyword_analysis.json` | BLOCKS Phase 3.5 | Keywords within budget limits, match types |
| **3.5. Service Validation** | `negative_keywords.json` | BLOCKS Phase 4 | **User confirms keywords match services** |
| 4. Campaign Structure | `campaign_structure.json` | BLOCKS Phase 5 | Campaigns, ad groups, split/consolidate |
| 5. Ad Copy | `ad_copy.json` | BLOCKS Phase 6 | Persona-targeted RSAs |
| 6. ROI Projection | `roi_calculator.json` | BLOCKS Phase 7 | Three scenarios, scaling roadmap |
| 7. Presentation | `presentation.html` | Final | Client deliverable |

---

## Phase 0: Discovery Interview

**Gate:** This phase MUST complete before ANY other work begins.

### Discovery UI Flow (REQUIRED STEPS)

Present these topics to the user AS SEPARATE STEPS. Do not combine them:

| Step | Topic | Questions to Ask |
|------|-------|------------------|
| 1 | **Budget** | Q3: Monthly Google Ads budget |
| 2 | **Customer Value** | Q1: What a typical customer spends |
| 3 | **Services to Advertise** | Q9: List ALL services to advertise (be specific - "Google Ads", not "marketing") |
| 4 | **Priority Focus** | Q2: Which 1-3 services should Google Ads focus on |
| 5 | **Geography** | Target location and language |
| 6 | **Exclusions** | Q7: What NOT to target, Q10: Services they DON'T offer or want to advertise |
| 7 | **Conversion Goal** | Q4: What counts as success (form, call, purchase) |
| 8 | **History** | Q5: Previous Google Ads experience |
| 9 | **Competition** | Q6: Who they lose customers to |
| 10 | **Context** | Q8: Additional notes, transcripts |

**CRITICAL:** Step 3 (Services to Advertise) and Step 6 (Exclusions including services NOT to advertise) are MANDATORY. They prevent keywords for services the business doesn't offer.

### Why This Phase Exists

Websites lie. Or at least, they don't tell the whole truth:
- The profitable service might not be prominently featured
- Client priorities ≠ website emphasis
- Budget determines everything else
- Past Google Ads history is invaluable
- Customer value drives all the math

**A senior PPC specialist always starts with a conversation, not a tool.**

### Required Questions

Use `AskUserQuestion` for each. These are NOT optional. Each answer drives concrete decisions.

**Question Groups:**
- **Q1-Q8:** Core discovery questions (ALWAYS ask)
- **Q9-Q10:** Service validation questions (ALWAYS ask - prevents wrong keywords)
- **Q11-Q13:** Positioning questions (CONDITIONAL - only for complex services)

---

#### Q1: Customer Value
**Ask:** "What does a typical customer spend with [client]? (First purchase value or annual value)"

**Why it matters:** Determines max CPC and ROI math.

**Decision it drives:**
```
Max CPC = Customer Value × Expected CVR × Close Rate ÷ Target ROAS

Example: 15,000 DKK × 5% × 20% ÷ 2.5 = 60 DKK max CPC
```

**Store as:** `$CUSTOMER_VALUE`
**Used in:** Phase 6 ROI projection, Phase 3 bid evaluation

---

#### Q2: Service Priority
**Ask:** "The website shows these services: [list from quick scan]. Which 1-3 should Google Ads focus on?"

**Why it matters:** Prevents spreading budget too thin.

**Decision it drives:**
| Priority Services | Campaign Structure |
|-------------------|-------------------|
| 1 service | Single campaign, deep keyword coverage |
| 2-3 services | 2-3 campaigns + brand |
| 4+ services | Discuss scope reduction or budget increase |

**Store as:** `$PRIORITY_SERVICES`
**Used in:** Phase 3 keyword focus, Phase 4 campaign structure

---

#### Q3: Budget
**Ask:** "What's the monthly Google Ads budget?"

**Why it matters:** Determines EVERYTHING about scope.

**Decision it drives:**
| Budget | Tier | Max Keywords | Match Types | Campaigns |
|--------|------|--------------|-------------|-----------|
| <3,000 DKK | Micro | 30-50 | 80% Exact, 20% Phrase | Brand + 1 theme |
| 3,000-10,000 DKK | Lean | 50-100 | 60% Phrase, 40% Exact | Brand + 2-3 themes |
| 10,000-30,000 DKK | Growth | 100-200 | 50% Phrase, 30% Exact, 20% Broad | Full coverage |
| >30,000 DKK | Scale | 200+ | 40% Phrase, 30% Broad, 30% Exact | Service + Geo splits |

**Store as:** `$BUDGET`, `$BUDGET_TIER`, `$MAX_KEYWORDS`
**Used in:** Phase 3 keyword limits, Phase 4 campaign count, Phase 6 projections

---

#### Q4: Conversion Goal
**Ask:** "What counts as a successful conversion? Form fill? Phone call? Purchase? Demo booking?"

**Why it matters:** Affects tracking setup, bid strategy, and ad copy CTAs.

**Decision it drives:**
| Conversion Type | Bid Strategy | CTA Style |
|-----------------|--------------|-----------|
| Form fills | Maximize Conversions → Target CPA | "Få tilbud", "Book samtale" |
| Phone calls | Call-focused, call extensions | "Ring nu", "Tal med os" |
| Purchases | Target ROAS | "Køb nu", "Bestil i dag" |
| Demo booking | Maximize Conversions | "Se demo", "Book demo" |

**Store as:** `$CONVERSION_GOAL`
**Used in:** Phase 4 bid strategy, Phase 5 CTAs

---

#### Q5: History
**Ask:** "Have they run Google Ads before? If yes, what happened?"

**Options:** Never tried / Tried and stopped / Currently running / Agency managed before

**Why it matters:** Learn from past mistakes, leverage what worked.

**Decision it drives:**
- If "tried and stopped" → Query RAG for common failure patterns
- If "currently running" → Request access to see what's working
- If "agency before" → Ask what they liked/disliked

**RAG Query (if history is negative):**
```python
query_knowledge(
    f"Why Google Ads campaigns fail for {business_type}",
    content_type="warning"
)
```

**Store as:** `$HISTORY`, `$HISTORY_LEARNINGS`
**Used in:** Strategy direction, things to avoid

---

#### Q6: Competition
**Ask:** "Who do they actually lose customers to? (Not who they think they compete with - who wins the deals)"

**Why it matters:** Real competitive intelligence for keyword gaps and positioning.

**Decision it drives:**
- Competitor keyword opportunities
- Positioning differentiation
- Whether to run competitor campaigns

**Store as:** `$COMPETITORS`
**Used in:** Phase 2 competitive analysis, Phase 3 competitor keywords

---

#### Q7: Exclusions
**Ask:** "Anything we should NOT target? Services, locations, customer types?"

**Why it matters:** Prevents wasted spend and misaligned leads.

**Decision it drives:**
- Negative keywords
- Campaign scope limits
- Geographic exclusions

**Store as:** `$EXCLUSIONS`
**Used in:** Phase 3 negative keywords, Phase 4 targeting

---

#### Q8: Additional Context (Optional)
**Ask:** "Any meeting notes, sales call transcripts, or other context I should know about?"

**Why it matters:** Captures nuance that questions miss.

**If provided, extract:**
- Explicit priorities mentioned ("we really want to push X")
- Pain points ("we've tried Y, it didn't work")
- Language they use (→ ad copy)
- Objections ("we don't want to compete on price")

**Cross-reference:** If transcript says "focus on A" but website emphasizes "B" → ASK for clarification.

**Store as:** `$ADDITIONAL_CONTEXT`
**Used in:** All phases (searchable reference)

---

---

### Service Validation Questions (Q9-Q10) - ALWAYS ASK

**These questions are MANDATORY for ALL businesses. They prevent the LinkedIn-type error.**

#### Q9: Services to Advertise
**Ask:** "List ALL services you want to advertise via Google Ads. Be specific - not 'marketing' but 'Google Ads management', 'Facebook Ads', etc."

**Why it matters:** Creates explicit source of truth for service validation. Prevents wrong keywords (e.g., LinkedIn keywords when they don't offer LinkedIn services).

**Decision it drives:**
- Canonical service list for keyword validation
- Campaign structure boundaries
- Service-to-landing-page mapping

**Store as:** `$SERVICES_TO_ADVERTISE`
**Used in:** Phase 1 Canonical Service List, Phase 3 keyword validation, Phase 3.5 service verification

---

#### Q10: Services NOT to Advertise
**Ask:** "Are there any services you offer but do NOT want to advertise? Or services people might search for that you explicitly DON'T provide?"

**Why it matters:** Catches potential keyword mismatches before research begins. More reliable than hoping to filter them out later.

**Example answers:**
- "We do websites but don't want to advertise them - focus on Google Ads only"
- "We don't offer LinkedIn advertising even though it's related to Meta Ads"
- "We serve B2B only - no consumer marketing"

**Store as:** `$SERVICES_NOT_TO_ADVERTISE`
**Used in:** Phase 3 keyword exclusion, Phase 3.5 validation, negative keyword generation

---

### Conditional Positioning Questions (Q11-Q13) - ONLY FOR COMPLEX SERVICES

**TRIGGER LOGIC:** Ask Q11-Q13 ONLY for complex services that sell outcomes, not commodities.

| Business Type | Ask Q11-Q13? | Rationale |
|---------------|--------------|-----------|
| Office hotel, plumber, moving | NO | Commodity search - just need to show up |
| E-commerce | NO | Product-focused, not outcome-focused |
| Consultant, coach, agency | YES | Sells outcomes, not ingredients |
| SaaS | YES | Sells transformation, not features |

**Detection:** Based on business type from quick website scan + Q2 answers.

```
IF business_type IN ['consultant', 'coach', 'agency', 'SaaS', 'professional_services']:
    SET $POSITIONING_MODE = 'deep'
    ASK Q11-Q13
ELSE:
    SET $POSITIONING_MODE = 'standard'
    SKIP Q11-Q13
```

---

#### Q11: Outcome vs. Ingredient (CONDITIONAL)
**Only ask if:** `$POSITIONING_MODE = 'deep'`

**Ask:** "What OUTCOME do you deliver to clients? Not the tools you use, but what they actually GET."

**Example answers:**
- "Filled calendars" (not "Google Ads management")
- "Predictable customer flow" (not "marketing services")
- "More revenue without more sales staff" (not "automation")

**Why it matters:** Identifies positioning keywords that differentiate from commodity keywords.

**Store as:** `$OUTCOME_PROMISE`
**Used in:** Phase 1 positioning-to-keyword translation, Phase 3 Pass 0

---

#### Q12: Positioning Language (CONDITIONAL)
**Only ask if:** `$POSITIONING_MODE = 'deep'`

**Ask:** "How do you describe what makes you different? What's your one-liner?"

**Example answers:**
- "We build systems, not campaigns"
- "One person, not an agency machine"
- "Infrastructure for growth, not quick fixes"

**Why it matters:** Exact language becomes ad copy differentiation AND keyword research seeds.

**Store as:** `$POSITIONING_LANGUAGE`
**Used in:** Phase 1 positioning translation, Phase 5 ad copy

---

#### Q13: Client Pain Points (CONDITIONAL)
**Only ask if:** `$POSITIONING_MODE = 'deep'`

**Ask:** "What frustration does your ideal client have BEFORE they find you?"

**Example answers:**
- "Unpredictable lead flow - feast or famine"
- "Wasted ad spend without knowing why"
- "Previous agencies that didn't understand their business"

**Why it matters:** Pain points become problem-aware keywords (mid-funnel) and ad copy hooks.

**Store as:** `$PAIN_POINTS`
**Used in:** Phase 1 problem keywords, Phase 3 Pass 2, Phase 5 ad copy

---

### Calculate Strategic Direction

After all questions answered, calculate and present:

```markdown
## Strategic Direction

Based on your answers:

| Input | Decision |
|-------|----------|
| Budget: $BUDGET | **$BUDGET_TIER tier** → Max $MAX_KEYWORDS keywords |
| Customer value: $CUSTOMER_VALUE | **Max CPC target:** ~$MAX_CPC DKK |
| Priority services: $PRIORITY_SERVICES | **Campaigns:** $CAMPAIGN_COUNT ($CAMPAIGN_LIST) |
| Conversion goal: $CONVERSION_GOAL | **Bid strategy:** $BID_STRATEGY |
| History: $HISTORY | **Watch out for:** $HISTORY_LEARNINGS |

### RAG Insights

[Query RAG for methodology and present key insights]

### Proposed Approach

1. [Campaign 1 purpose and focus]
2. [Campaign 2 purpose and focus]
3. [Brand campaign]

**Does this direction make sense before I proceed?**
```

### RAG Integration

Query RAG after discovery to inform strategy:

```python
# Get methodology for this business type
methodology = query_knowledge(
    f"Google Ads campaign strategy for {business_type}",
    content_type="methodology"
)

# If history is negative, get warnings
if history == "Tried and stopped":
    warnings = query_knowledge(
        f"Common Google Ads mistakes {business_type}",
        content_type="warning"
    )

# Get similar client examples
examples = list_examples()
similar = get_example(most_similar_client)
```

### Output Artifact: `discovery_brief.md`

Use template from `templates/discovery_brief.md`. Must contain:

- All 8 answers stored as variables
- Calculated decisions (budget tier, max keywords, max CPC)
- RAG insights retrieved
- Strategic direction confirmed by user

### Checkpoint

Before proceeding to Phase 1, verify:
- [ ] Q1-Q7 answered (core questions)
- [ ] Q8 answered (optional but recommended)
- [ ] **Q9-Q10 answered (mandatory service validation questions)**
- [ ] **Q11-Q13 answered IF `$POSITIONING_MODE = 'deep'`** (skip for commodity businesses)
- [ ] Budget tier calculated with keyword limits
- [ ] Max CPC calculated from customer value
- [ ] `$SERVICES_TO_ADVERTISE` and `$SERVICES_NOT_TO_ADVERTISE` documented
- [ ] RAG queried for methodology and warnings
- [ ] Strategic direction presented and confirmed
- [ ] `discovery_brief.md` created

**If any checkbox is incomplete: STOP. Do not proceed.**

---

## Phase 1: Business Deep-Dive

**Prerequisite:** Phase 0 `discovery_brief.md` must exist.

**Gate:** This phase validates discovery answers against the actual website.

### Purpose

Phase 0 gave us client input. Phase 1 validates and enriches with website analysis.

### Strategic Framework

305. **Validate business type** against Phase 0 hypothesis by reading `decision-trees/business-type-detection.md` and applying its rules:

| Business Type | Detection Signals | Campaign Strategy |
|---------------|-------------------|-------------------|
| **Local Service** | Physical address, "near me", service area | Brand + Service + Emergency |
| **E-commerce** | Product catalog, cart, checkout | Shopping/PMax + Category + Brand |
| **Lead Gen (B2B)** | Contact form, demo request, "get quote" | Brand + High-Intent + Problem-Aware |
| **SaaS** | Free trial, pricing page, features | Brand + Product + Problem + Competitor |
| **Agency/Consultancy** | Services page, case studies, team | Brand + Service + Outcome |

### Actions

1. **Fetch and discover website structure** using WebFetch

   **Step 1:** Fetch the homepage URL provided by user

   **Step 2:** Extract ALL internal links from the homepage HTML:
   - Look in `<nav>` elements for navigation links
   - Look in `<footer>` for sitemap-style links
   - Look for service/product links in the main content
   - **CRITICAL: Do NOT guess URLs - only use links found in HTML**

   **Step 3:** Try fetching `/sitemap.xml` - if it exists, extract additional URLs

   **Step 4:** From discovered links, fetch key pages:
   - Service/product pages (prioritize `$PRIORITY_SERVICES` from Phase 0)
   - About page (if found)
   - Contact page (if found)
   - Pricing page (if found)

   **Step 5:** If important pages seem missing, ask user:
   - "I found these pages: [list]. Are there other service pages I should review?"

2. **Build Canonical Service List** (CRITICAL - prevents wrong keywords)

   Cross-reference `$SERVICES_TO_ADVERTISE` from Q9 with website content to create explicit service list:

   ```markdown
   ## Canonical Service List

   This is the SOURCE OF TRUTH for what services to target with keywords.

   | Service ID | Service Name | Landing Page | Keyword Variations |
   |------------|--------------|--------------|-------------------|
   | SVC-001 | Google Ads | /kundeflow/google-ads | AdWords, SEM, PPC |
   | SVC-002 | Meta Ads | /kundeflow/meta-ads | Facebook Ads, Instagram Ads |
   | SVC-003 | Lead Generation | /kundeflow/leadgenerering | B2B leads, leadgen |

   ## Services NOT Offered (from Q10 + website analysis)

   | Service | Why Not | Action |
   |---------|---------|--------|
   | LinkedIn Ads | No landing page, not mentioned in Q9 | EXCLUDE keywords |
   | TikTok Ads | Not mentioned, no page | EXCLUDE keywords |
   | SEO | Mentioned on site but NOT in Q9 | EXCLUDE keywords |
   ```

   **Validation Rules:**
   - Every service in `$SERVICES_TO_ADVERTISE` MUST have a landing page
   - Services found on website but NOT in `$SERVICES_TO_ADVERTISE` → Ask user before including
   - Services in `$SERVICES_NOT_TO_ADVERTISE` → Add to exclusion list
   - Platform-specific services (LinkedIn, TikTok, Twitter) → Only include if explicitly in Q9

   **Store as:** `$CANONICAL_SERVICES`, `$SERVICES_NOT_OFFERED`
   **Used in:** Phase 3 keyword validation, Phase 3.5 service verification, Phase 4 campaign structure

3. **Validate business type** against Phase 0 hypothesis:
   - [ ] Physical address visible? → Local Service signal
   - [ ] Product catalog/SKUs? → E-commerce signal
   - [ ] "Get quote" / "Contact us" primary CTA? → Lead Gen signal
   - [ ] Free trial / pricing tiers? → SaaS signal
   - [ ] Services page + case studies? → Agency signal

3. **Cross-reference with Phase 0:**
   - Do `$PRIORITY_SERVICES` have dedicated landing pages?
   - Does website emphasis match client priorities?
   - **Flag discrepancies:** "You mentioned [X] as priority, but website emphasizes [Y]. Which is correct?"

4. **Map buyer journey** - For each priority service:
   - **PROBLEM keywords** - What pain does customer have?
   - **SOLUTION keywords** - What are they looking for?
   - **PROOF keywords** - How do they validate?
   - **ACTION keywords** - How do they convert?

5. **Audit landing pages:**
   - Does each `$PRIORITY_SERVICE` have a landing page?
   - Has form/conversion action matching `$CONVERSION_GOAL`?
   - **Red flag:** >50% of keywords would land on homepage → STOP and discuss

6. **Extract positioning:**
   - What makes them different? (not just "what do they sell")
   - Use language from `$ADDITIONAL_CONTEXT` if provided

7. **Identify competitor signals:**
   - Cross-reference with `$COMPETITORS` from Phase 0
   - Any competitor mentions on the site?

8. **CRITICAL: Translate Positioning → Keyword Strategy**

   This step is the BRIDGE between discovery and keyword research. Without it, you'll produce generic commodity keywords.

   For EACH positioning element, define:

   | Positioning | Problem Keywords | Outcome Keywords | Differentiation Keywords |
   |-------------|------------------|------------------|-------------------------|
   | "Systems, not campaigns" | "marketing kaos", "ingen struktur", "ad hoc marketing" | "forudsigelig leadgenerering", "stabil kundetilgang" | "systembaseret marketing", "marketing system" |
   | "Predictable customer flow" | "uforudsigelig kundetilgang", "op og ned med kunder" | "konstant flow af kunder", "fyldt kalender" | "kundeflow system", "forudsigelig pipeline" |

   **Store in `$POSITIONING_KEYWORDS`** - This becomes the FIRST research target in Phase 3.

   **Example for Monday Brew:**
   ```
   POSITIONING: "Vi bygger systemer, ikke kampagner"

   Problem keywords to research:
   - "marketing uden struktur"
   - "uforudsigelig kundetilgang"
   - "op og ned med kunder"
   - "ingen faste leads"

   Outcome keywords to research:
   - "forudsigelig leadgenerering"
   - "stabil kundetilgang"
   - "fyldt kalender hver måned"
   - "vækst uden kaos"

   Differentiation keywords:
   - "systembaseret marketing"
   - "marketing system"
   - "struktureret leadgenerering"
   ```

   **These keywords may have LOW or ZERO volume** - that's OK. They reflect true positioning. In Phase 3, you'll:
   1. Research these first (Pass 0)
   2. Find related terms that DO have volume
   3. Build outward from positioning, not inward from commodities

### RAG Integration

```python
# Get methodology for detected business type
methodology = get_methodology("keyword_research")

# Query for business-type specific best practices
practices = query_knowledge(
    f"Best practices for {business_type} Google Ads",
    content_type="best_practice"
)
```

### Output Artifact: `website_content.md`

Use template from `templates/website_content.md`. Include:
- Business type classification (validated)
- **`$CANONICAL_SERVICES`** - The explicit service list with IDs, landing pages, and variations (REQUIRED)
- **`$SERVICES_NOT_OFFERED`** - Services to exclude from keyword research (REQUIRED)
- Services mapped to landing pages
- Buyer journey keywords per service
- USPs with headline versions
- Cross-reference with Phase 0 findings
- Any discrepancies flagged
- **`$POSITIONING_KEYWORDS`** - The positioning-to-keyword translation table (REQUIRED if `$POSITIONING_MODE = 'deep'`)

### Checkpoint

Before proceeding to Phase 2, verify:
- [ ] Website fetched and analyzed
- [ ] **Canonical Service List created** with Service IDs and landing pages
- [ ] **Services NOT Offered documented** (from Q10 + website analysis)
- [ ] Business type validated against Phase 0
- [ ] Priority services have landing pages (or flagged)
- [ ] Buyer journey mapped (Problem → Solution → Proof → Action)
- [ ] No major discrepancies between Phase 0 and website
- [ ] **Positioning → Keyword translation completed** (if `$POSITIONING_MODE = 'deep'`)

**If Canonical Service List is missing: STOP. This prevents the LinkedIn-type errors.**

---

## Phase 2: Strategic Analysis

**Prerequisite:** Phase 1 `website_content.md` must exist.

### Purpose

Synthesize Phase 0 (client input) and Phase 1 (website analysis) into strategic direction.

### Actions

1. **Synthesize findings** into strategic document

2. **Define buyer personas** (2-3 based on `$PRIORITY_SERVICES`):
   - **High-intent persona** - Ready to buy, searching for specific solution
   - **Research persona** - Comparing options, searching for information
   - **Problem-aware persona** - Knows pain, doesn't know solution exists

3. **Build keyword opportunity matrix:**
   - Volume × Intent × Competition
   - Prioritize based on `$BUDGET_TIER`

4. **Define campaign segmentation:**
452. **Review logic** in `decision-trees/campaign-split-logic.md` for split/consolidate decisions.
   - Respect `$MAX_KEYWORDS` and campaign limits from Phase 0
   - B2B vs B2C split? (ALWAYS split if both exist)

5. **Competitive analysis:**
   - Use `$COMPETITORS` from Phase 0
   - Identify gaps and positioning opportunities

### RAG Integration

```python
# Get similar client examples
examples = list_examples()
similar_example = get_example("most_similar_client")

# Query competitive strategy
competitive = query_knowledge(
    f"Competitive positioning {industry}",
    content_type="methodology"
)
```

### Output Artifact: `potential_analysis.md`

Use template from `templates/potential_analysis.md`. Include:
- Executive summary with Phase 0 constraints
- Buyer personas (2-3)
- Campaign segmentation with rationale
- Competitive landscape
- Preliminary ROI estimate using `$CUSTOMER_VALUE`

### Checkpoint

- [ ] Buyer personas defined (aligned with priority services)
- [ ] Campaign segmentation respects budget tier limits
- [ ] Competitive gaps identified
- [ ] RAG examples consulted

---

## Phase 3: Keyword Research (Budget-Aware)

**Prerequisite:** Phase 2 `potential_analysis.md` must exist.

**CRITICAL:** Budget-first approach. Check `$MAX_KEYWORDS` before starting.

### Strategic Framework

**BEFORE any research, confirm from Phase 0:**
- `$BUDGET_TIER` → Max keyword count
- `$MAX_CPC` → Filter out keywords with bids above this
- `$PRIORITY_SERVICES` → Focus research here

| Budget Tier | Max Keywords | Match Type Bias | Research Depth |
|-------------|--------------|-----------------|----------------|
| Micro | 30-50 | 80% Exact, 20% Phrase | Priority service only |
| Lean | 50-100 | 60% Phrase, 40% Exact | 2-3 services |
| Growth | 100-200 | 50% Phrase, 30% Exact, 20% Broad | Full coverage |
| Scale | 200+ | 40% Phrase, 30% Broad, 30% Exact | Full + geo + competitor |

### Actions

1. **FIRST: Positioning-Aware Research (from Phase 1 `$POSITIONING_KEYWORDS`)**

   **Pass 0: Positioning keywords** (MANDATORY - do this BEFORE generic passes)

   Research the exact keywords from the positioning translation table:

   ```python
   # Example for Monday Brew
   positioning_keywords = [
       # Problem keywords from positioning
       "marketing uden struktur", "uforudsigelig kundetilgang",
       "op og ned med kunder", "ingen faste leads",
       # Outcome keywords from positioning
       "forudsigelig leadgenerering", "stabil kundetilgang",
       "fyldt kalender", "vækst uden kaos",
       # Differentiation keywords
       "systembaseret marketing", "marketing system"
   ]

   results = kp.generate_keyword_ideas(
       keywords=positioning_keywords,
       location_ids=[2208],
       language_id="1009"
   )
   ```

   **Expected outcome:** Many of these will have low/zero volume. That's FINE. The goal is to find RELATED terms that DO have volume but still reflect the positioning.

   **Store results separately:** These are your differentiated keywords. They should be tagged with `Positioning: true` in the output.

2. **THEN: Research by Buyer Journey Stage (from Phase 1)**

   **Pass 1: Solution keywords** (high-intent core) - `$PRIORITY_SERVICES`

   **Pass 2: Problem keywords** (mid-funnel) - Pain points from buyer journey

   **Pass 3: Proof keywords** (consideration) - Reviews, comparisons

   **Pass 4: Action keywords** (conversion) - Book, price, quote

   **Pass 5: Location × Service** (if local business)

   **Pass 6: Misspellings** (top performers only)

3. **Apply Match Type Thresholds** from `decision-trees/match-type-strategy.md`

4. **Filter by `$MAX_CPC`:**
   - Keywords with high-range bid > 2× `$MAX_CPC` → Flag or exclude
   - Keywords with low-range bid > `$MAX_CPC` → Review carefully

5. **Generate Negative Keyword Lists** by reading `decision-trees/negative-keywords.md`:
   - Layer 1: Global (gratis, billig, DIY, etc.)
   - Layer 2: Vertical-specific (based on business type)
   - Layer 3: `$EXCLUSIONS` from Phase 0

6. **Tag Each Keyword** with:
   - Category (from Phase 2)
   - Intent (High/Medium/Low)
   - Buyer Journey (Problem/Solution/Proof/Action)
   - Match Type Rationale
   - **Positioning (true/false)** - Keywords from Pass 0 that reflect unique positioning

### RAG Integration

```python
# Get match type best practices
match_types = query_knowledge(
    f"Match type strategy {budget_tier} budget",
    content_type="best_practice"
)

# Get CPC benchmarks
benchmarks = query_knowledge(
    f"CPC benchmarks {industry} {country}",
    content_type="example"
)
```

### Stop Criteria

Stop when:
- **Positioning keywords researched FIRST** (Pass 0 completed)
- At least 10-20% of keywords are positioning-aligned (tagged `Positioning: true`)
- All `$PRIORITY_SERVICES` have keyword coverage
- Total keywords ≤ `$MAX_KEYWORDS`
- Avg volume per keyword >200
- No new themes emerging

### Output Artifact: `keyword_analysis.json`

Include `Match Type Rationale` for each keyword.

### Checkpoint

- [ ] **Pass 0 (Positioning keywords) completed BEFORE generic passes**
- [ ] **At least 10-20% of keywords tagged `Positioning: true`**
- [ ] Keywords within `$MAX_KEYWORDS` limit
- [ ] Match types varied with rationale
- [ ] High-bid keywords filtered against `$MAX_CPC`
- [ ] All `$PRIORITY_SERVICES` covered
- [ ] Avg volume per keyword >200

**If positioning keywords are missing or <10% of total: STOP. Go back to Pass 0.**

---

## Phase 3.5: Pre-Finalization Review (Service Validation)

**Prerequisite:** Phase 3 `keyword_analysis.json` must exist.

**Gate:** This phase validates keywords against `$CANONICAL_SERVICES` before building campaigns.

### Why This Phase Exists

URL-based keyword research returns related keywords that may not match actual services offered. This causes errors like:
- "annoncering på linkedin" appearing when business doesn't offer LinkedIn services
- "ecommerce marketing" when business focuses on B2B only
- Service platforms being miscategorized (LinkedIn ≠ Meta)

**This checkpoint catches these errors with user confirmation.**

### Actions

1. **Service Validation Check**

   For EVERY keyword in `keyword_analysis.json`, validate against `$CANONICAL_SERVICES`:

   ```python
   for keyword in keywords:
       matched_service = match_keyword_to_service(keyword, canonical_services)
       if matched_service is None:
           flag_for_review(keyword)
   ```

   **Matching rules:**
   - "google ads bureau" → SVC-001 (Google Ads) ✓
   - "facebook annoncering" → SVC-002 (Meta Ads) ✓
   - "annoncering på linkedin" → NO MATCH → Flag for review
   - "ecommerce marketing" → NO MATCH (if not in services) → Flag for review

2. **Present Mismatches to User**

   For any unmatched keywords, present them explicitly:

   ```markdown
   ## Service Validation Required

   I found keywords that don't match your documented services from Q9:

   | Keyword | Detected Service | Your Services | Recommendation |
   |---------|------------------|---------------|----------------|
   | "annoncering på linkedin" | LinkedIn Ads | Not in Q9 | Exclude? |
   | "tiktok marketing bureau" | TikTok Ads | Not in Q9 | Exclude? |
   | "ecommerce google ads" | E-commerce | B2B only (Q10) | Exclude? |

   **Question:** Should I exclude these keywords, or do you actually offer these services?

   Options:
   1. Exclude all (they're not services we offer)
   2. Include [specific ones] (we do offer those, update Q9)
   3. Let me clarify which services we offer
   ```

3. **Update Based on Response**

   - If "Exclude all" → Remove from keyword list, add to negative keywords
   - If "Include specific" → Update `$CANONICAL_SERVICES` and keep keywords
   - If "Clarify" → Return to Q9/Q10 and update

4. **Validate Negative Keywords**

   Confirm negative keyword layers are complete:

   ```markdown
   ## Negative Keyword Review

   I've generated negative keywords in 3 layers:

   **Layer 1 (Global):** gratis, billig, DIY, selv, job, karriere, løn...
   **Layer 2 (Vertical):** [based on business type]
   **Layer 3 (Client-specific):** [from Q7 + Q10 exclusions]
   **Layer 4 (Campaign-specific):** [cross-campaign negatives]

   Does this look complete? Any terms to add?
   ```

### Output Updates

After validation:
- Update `keyword_analysis.json` with excluded keywords marked `Include: false`
- Create/update `negative_keywords.json` with structured 3-layer format

### Output Artifact: `negative_keywords.json` (NEW)

```json
{
  "global": ["gratis", "billig", "DIY", "selv", "pdf", "job", "karriere", "løn", "praktik", "uddannelse", "kursus", "hvad er", "wikipedia"],
  "vertical": ["consumer", "privat", "home", "student"],
  "client_specific": ["webshop", "online shop", "e-handel", "ecommerce"],
  "campaign_specific": {
    "mb | DA | Search | Google Ads": ["facebook", "instagram", "meta", "linkedin"],
    "mb | DA | Search | Meta Ads": ["google", "adwords", "linkedin"]
  }
}
```

### Checkpoint

Before proceeding to Phase 4, verify:
- [ ] All keywords validated against `$CANONICAL_SERVICES`
- [ ] Mismatched keywords presented to user and resolved
- [ ] User confirmed service coverage is correct
- [ ] `negative_keywords.json` created with 3+ layers
- [ ] Keywords from `$SERVICES_NOT_TO_ADVERTISE` excluded

**If service mismatches exist but were not confirmed: STOP. Get user approval.**

---

## Phase 4: Campaign Structure

**Prerequisite:** Phase 3.5 service validation must be complete.

### Strategic Framework

Respect constraints from Phase 0:
- Campaign count within budget tier limits
- Landing pages for `$PRIORITY_SERVICES`
- Bid strategy aligned with `$CONVERSION_GOAL`

Use `decision-trees/campaign-split-logic.md` for split/consolidate decisions.

### Actions

1. **Map keywords to ad groups** (5-15 keywords max per ad group)

2. **Apply naming conventions:**
   - Campaign: `mb | {LANG} | {Type} | {Theme}`
   - Ad group: `{Theme} | {Location}`

3. **Assign landing pages:**
   - Use SPECIFIC pages from Phase 1 audit
   - Match to `$PRIORITY_SERVICES`

4. **Recommend bid strategies** based on `$CONVERSION_GOAL`:
   - Form fills/Calls → Maximize Conversions → Target CPA
   - Purchases → Target ROAS
   - New campaigns → Maximize Conversions (learning phase)

### Output Artifact: `campaign_structure.json`

Include `Split Rationale` for each campaign.

### Checkpoint

- [ ] Campaign count within budget tier limits
- [ ] Landing pages are specific (not homepage)
- [ ] Bid strategy matches `$CONVERSION_GOAL`
- [ ] Split/consolidate rationale documented

---

## Phase 5: Ad Copy (Persona-Based + Ad Group Differentiated)

**Prerequisite:** Phase 4 `campaign_structure.json` must exist.

### Strategic Framework

Create ad copy **per buyer persona** from Phase 2, with CTAs matching `$CONVERSION_GOAL`.

**CRITICAL: Each ad group must have UNIQUE headlines.** Do NOT copy-paste the same headlines across ad groups.

| Persona | H1 Focus | Description Focus | CTA Style |
|---------|----------|-------------------|-----------|
| High-intent | {KeyWord} + benefit | Process + speed | Based on `$CONVERSION_GOAL` |
| Research | Category + differentiator | Why us | "Læs mere", "Se hvordan" |
| Problem-aware | Pain acknowledgment | Outcomes | "Få hjælp", "Løs problemet" |

### Ad Group Differentiation Rules (NEW)

**The mondaybrew mistake:** Same 6 headlines used across all ad groups. This makes all ads feel generic.

**The fix:** Each ad group should have headlines specific to its theme.

**How to differentiate:**

1. **H1: Always different** - Use DKI with ad-group-specific fallback
   - Ad Group "Google Ads": `{KeyWord:Google Ads specialist}`
   - Ad Group "CRM": `{KeyWord:CRM system til B2B}`
   - Ad Group "Websites": `{KeyWord:Professionelle hjemmesider}`

2. **H2-H3: Theme-specific benefits**
   - Google Ads ad group: "Flere leads, lavere CPC", "Data-drevet optimering"
   - CRM ad group: "Al kundekontakt ét sted", "Aldrig tab et lead"
   - Website ad group: "Konverterende design", "SEO-optimeret fra start"

3. **H4-H6: Can overlap if truly universal**
   - Only repeat headlines that apply to ALL ad groups
   - USPs, trust signals, general CTAs can be shared
   - But at least 3 headlines MUST be unique per ad group

4. **Descriptions: At least D1 unique per ad group**
   - D1 should describe the specific service
   - D2-D4 can overlap if relevant to all

### CTA Mapping (from `$CONVERSION_GOAL`)

| Conversion Goal | CTAs to Use |
|-----------------|-------------|
| Form fills | "Få tilbud", "Book samtale", "Kontakt os" |
| Phone calls | "Ring nu", "Tal med os i dag" |
| Purchases | "Køb nu", "Bestil i dag" |
| Demo booking | "Se demo", "Book demo", "Prøv gratis" |

### Actions

1. **Create RSAs** with 6-10 quality headlines (not 15 padding)
2. **Apply DKI** in Headline 1, pin to position 1
3. **Use language from `$ADDITIONAL_CONTEXT`** if provided
4. **Match CTAs** to `$CONVERSION_GOAL`

### Output Artifact: `ad_copy.json`

Include `Persona Target` for each ad group.

### Differentiation Validation (NEW)

Before finishing Phase 5, validate:

```
For each ad group:
1. Count unique headlines (not used in any other ad group)
2. Unique count must be >= 3

If unique < 3: Rewrite headlines to reflect ad group theme.
```

**Example validation:**

| Ad Group | Total Headlines | Unique Headlines | Status |
|----------|-----------------|------------------|--------|
| Google Ads | 8 | 4 | ✓ Pass |
| CRM | 8 | 5 | ✓ Pass |
| Websites | 8 | 2 | ✗ FAIL - Need more unique |

### Checkpoint

- [ ] CTAs match `$CONVERSION_GOAL`
- [ ] Sentence case applied
- [ ] Persona targeting documented
- [ ] Client language used (from `$ADDITIONAL_CONTEXT`)
- [ ] **Each ad group has at least 3 unique headlines** (not shared with other ad groups)
- [ ] **H1 fallback text is specific to each ad group**
- [ ] **D1 describes the specific service of that ad group**

**If ad groups share too many headlines: STOP. Rewrite to differentiate.**

---

## Phase 6: ROI Projection

**Prerequisite:** Phase 5 `ad_copy.json` must exist.

### Strategic Framework

Use `$CUSTOMER_VALUE` and `$BUDGET` from Phase 0 for projections.

### Calculations

```
Monthly clicks = $BUDGET ÷ Avg CPC (from Phase 3)
Monthly leads = Clicks × CVR (5% default for B2B)
Monthly customers = Leads × Close rate (20% default)
Revenue = Customers × $CUSTOMER_VALUE
ROAS = Revenue ÷ $BUDGET
```

### Three Scenarios

| Scenario | CVR | Close Rate | When It Happens |
|----------|-----|------------|-----------------|
| Conservative | 3% | 15% | Poor landing pages, weak follow-up |
| Expected | 5% | 20% | Standard performance |
| Optimistic | 8% | 25% | Optimized funnel |

### Break-Even Analysis

```
Min Customer Value for Profitability = $BUDGET ÷ Expected Customers
```

If actual `$CUSTOMER_VALUE` > min, campaign is profitable.

### RAG Integration

```python
# Get conversion rate benchmarks
benchmarks = query_knowledge(
    f"Conversion rate benchmark {business_type}",
    content_type="example"
)
```

### Output Artifacts

- `roi_calculator.json` - Three scenarios with assumptions
- `scaling_roadmap.md` - When to increase budget, what to add

### Checkpoint

- [ ] Three scenarios calculated
- [ ] `$CUSTOMER_VALUE` used in projections
- [ ] Break-even analysis completed
- [ ] Scaling roadmap created

---

## Phase 7: Presentation

**Prerequisite:** Phase 6 `roi_calculator.json` must exist.

### Actions

1. **Run presentation generator:**
   ```bash
   python scripts/generate_presentation.py clients/{client-name}
   ```

2. **Verify all tabs populated:**
   - Executive Summary (from `potential_analysis.md`)
   - ROI Calculator (from `roi_calculator.json`)
   - Keywords (from `keyword_analysis.json`)
   - Campaigns (from `campaign_structure.json`)
   - Ads (from `ad_copy.json`)

### Output Artifact: `presentation.html`

### Final Delivery

1. **Primary:** `clients/{client-name}/presentation.html`
2. **Optional:** Google Sheet with 4 tabs
3. **Validation:** `python scripts/validate_output.py clients/{client-name}`

---

## Decision Flow Summary

```
Phase 0 Discovery
│
├─ Q1: Customer Value ──────→ Max CPC calculation (Phase 3, 6)
├─ Q2: Priority Services ───→ Keyword focus, campaign structure (Phase 3, 4)
├─ Q3: Budget ──────────────→ Keyword limits, match types (Phase 3)
├─ Q4: Conversion Goal ─────→ Bid strategy, CTAs (Phase 4, 5)
├─ Q5: History ─────────────→ RAG warnings query, strategy (All)
├─ Q6: Competition ─────────→ Competitive keywords (Phase 2, 3)
├─ Q7: Exclusions ──────────→ Negative keywords (Phase 3)
├─ Q8: Context ─────────────→ Ad copy language (Phase 5)
├─ Q9: Services to Advertise → Canonical Service List (Phase 1, 3.5)
├─ Q10: Services NOT to Advertise → Exclusion list (Phase 3, 3.5)
│
└─ [IF $POSITIONING_MODE = 'deep']
   ├─ Q11: Outcome Promise ──→ Positioning keywords (Phase 3 Pass 0)
   ├─ Q12: Positioning Language → Ad copy, differentiation (Phase 5)
   └─ Q13: Pain Points ──────→ Problem keywords (Phase 3 Pass 2)
```

---

## RAG Integration Summary

| When | Query | Purpose |
|------|-------|---------|
| Phase 0 (after discovery) | `get_methodology("keyword_research")` | Inform strategy |
| Phase 0 (if history negative) | `query_knowledge("failures", content_type="warning")` | Avoid mistakes |
| Phase 1 (business type) | `query_knowledge("best practices {type}")` | Type-specific guidance |
| Phase 2 (strategy) | `get_example(similar_client)` | Pattern matching |
| Phase 3 (match types) | `query_knowledge("match type strategy")` | Validate decisions |
| Phase 6 (ROI) | `query_knowledge("CVR benchmarks")` | Reality check |

---

## Additional Resources

### Decision Trees
- `decision-trees/business-type-detection.md`
- `decision-trees/budget-tiers.md`
- `decision-trees/match-type-strategy.md`
- `decision-trees/negative-keywords.md`
- `decision-trees/campaign-split-logic.md`

### Templates
- `templates/discovery_brief.md` (NEW)
- `templates/website_content.md`
- `templates/potential_analysis.md`

### Golden Example
- `examples/aeflyt/` - Complete example of all artifacts
