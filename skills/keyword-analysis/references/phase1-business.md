# Phase 1: Business Understanding Reference

Detailed guide for extracting business information and detecting business type.

---

## Business Type Detection

**FIRST STEP:** Classify the business type to determine campaign strategy.

See `decision-trees/business-type-detection.md` for full decision flow.

### Quick Detection Checklist

| Signal | Business Type |
|--------|--------------|
| Physical address, service area | Local Service |
| Product catalog, cart/checkout | E-commerce |
| Contact form as primary CTA | Lead Gen (B2B) |
| Free trial, pricing tiers | SaaS |
| Services page, case studies | Agency/Consultancy |

### Output Required

Document in `website_content.md`:
```markdown
## Business Type Classification

**Primary Type:** [Type]

**Detection Signals:**
- [Signal 1] (✓)
- [Signal 2] (✓)

**Campaign Strategy Implication:**
- [Strategy notes]
```

---

## Website Analysis Checklist

### Services/Products

- [ ] List ALL services or products offered
- [ ] Identify PRIMARY services (main revenue drivers)
- [ ] Identify SECONDARY services (add-ons, upsells)
- [ ] Note any services to EXCLUDE from advertising
- [ ] Check pricing pages for service tiers

### Geographic Scope

- [ ] Local only (single city/area)?
- [ ] Regional (state/region)?
- [ ] National?
- [ ] International?
- [ ] Check "Areas We Serve" or "Locations" pages

### Target Customers

- [ ] B2B (businesses)?
- [ ] B2C (consumers)?
- [ ] Both? → MUST split campaigns
- [ ] Specific industries or demographics mentioned?

### Unique Selling Propositions (USPs)

- [ ] What makes them different from competitors?
- [ ] Certifications or credentials?
- [ ] Years of experience?
- [ ] Guarantees or warranties?
- [ ] Special processes or technology?

**Example USP Extraction:**
```
Website says: "Vi bygger systemer, ikke kampagner"
USP 1: System-based approach (not one-off campaigns)
USP 2: Long-term partnership model
```

### Brand Voice & Messaging

- [ ] Formal or casual tone?
- [ ] Key phrases or taglines?
- [ ] Emotional appeal (trust, care, speed, value)?
- [ ] Technical vs. accessible language?

### Positioning

**Critical:** Identify what makes them DIFFERENT, not just what they SELL.

| Business | What They Sell | What Makes Them Different |
|----------|---------------|---------------------------|
| mondaybrew | Marketing services | "Systems, not campaigns" |
| Aeflyt | Moving services | "Flytning med kærlig hånd" |
| Spacefinder | Office space | "Norges største kontormarked" |

---

## Positioning → Keyword Translation (CRITICAL)

**This is the BRIDGE between discovery and keyword research.**

Without this step, you'll produce generic commodity keywords that any competitor would target.

### The Translation Table

For EACH positioning element, define three types of keywords:

| Type | Definition | Example (mondaybrew) |
|------|------------|---------------------|
| **Problem** | What pain does customer have RELATED to positioning | "marketing uden struktur", "uforudsigelig kundetilgang" |
| **Outcome** | What result does positioning promise | "forudsigelig leadgenerering", "stabil kundetilgang" |
| **Differentiation** | How positioning is described as a keyword | "systembaseret marketing", "marketing system" |

### Example: mondaybrew

**Positioning:** "Vi bygger systemer, ikke kampagner"

```markdown
## Positioning → Keyword Translation

### Positioning Element: "Systems, not campaigns"

| Type | Keywords to Research |
|------|---------------------|
| Problem | "marketing uden struktur", "ad hoc marketing", "ingen rød tråd i marketing" |
| Outcome | "struktureret marketing", "forudsigelig leadgenerering" |
| Differentiation | "systembaseret marketing", "marketing system", "marketing infrastruktur" |

### Positioning Element: "Predictable customer flow"

| Type | Keywords to Research |
|------|---------------------|
| Problem | "uforudsigelig kundetilgang", "op og ned med kunder", "ingen faste leads" |
| Outcome | "stabil kundetilgang", "fyldt kalender", "konstant flow af kunder" |
| Differentiation | "kundeflow system", "forudsigelig pipeline" |
```

### Why This Matters

**Without translation:**
- Keywords: "marketing bureau", "google ads bureau", "webbureau"
- Result: Same keywords as every competitor

**With translation:**
- Keywords: "forudsigelig leadgenerering", "marketing system", "struktureret kundetilgang"
- Result: Keywords that attract customers looking for YOUR specific value

### Volume Reality Check

Many positioning keywords will have LOW or ZERO volume. That's expected.

**What to do:**
1. Research these keywords in Pass 0
2. Find RELATED terms that DO have volume
3. Tag them with `Positioning: true` so they're prioritized

### Store as `$POSITIONING_KEYWORDS`

This table becomes the FIRST research target in Phase 3.

---

## Landing Page Audit (NEW)

**Before keyword research, audit what landing pages exist.**

### Audit Checklist

For each service:
- [ ] Does a dedicated landing page exist?
- [ ] What's the URL structure? (/{service}/ or /services/{service}/)
- [ ] Is there a contact form on the page?
- [ ] What conversion action is available? (form, phone, chat)
- [ ] Is the page optimized for the service?

### Red Flag

**If >50% of keywords will land on homepage, STOP and discuss with user.**

Options:
1. Create service-specific landing pages first
2. Limit campaign scope to services with landing pages
3. Use homepage but expect lower Quality Scores

### Output: `landing_page_audit.md`

```markdown
# Landing Page Audit: {Client Name}

## Available Landing Pages

| Service | URL | Has Form | Status |
|---------|-----|----------|--------|
| Google Ads | /google-ads/ | Yes | Ready |
| CRM | /crm/ | Yes | Ready |
| Websites | /websites/ | No | Needs form |

## Missing Pages

- **Email Marketing**: No dedicated page. Using /services/ (not ideal)
- **SEO**: No page exists. Exclude from campaign.

## Recommendations

1. Add contact form to /websites/
2. Create /email-marketing/ page before targeting
3. Exclude SEO until page is created
```

---

## Buyer Journey Mapping (NEW)

**Map keywords by buyer journey stage for each service.**

### Four Stages

| Stage | What Searcher Thinks | Keyword Examples |
|-------|---------------------|------------------|
| **PROBLEM** | "I have a problem" | "uforudsigelig kundetilgang", "hvorfor får jeg ikke leads" |
| **SOLUTION** | "What's the solution?" | "marketing bureau", "google ads bureau" |
| **PROOF** | "Does it work?" | "google ads bureau anmeldelser", "marketing bureau case" |
| **ACTION** | "How do I start?" | "book møde marketing", "få tilbud google ads" |

### Example Mapping

**Service: Google Ads Management**

```
PROBLEM keywords:
- "mine google ads virker ikke"
- "for dyrt cost per lead"
- "google ads ingen konverteringer"

SOLUTION keywords:
- "google ads bureau"
- "google ads specialist"
- "professionel google ads"

PROOF keywords:
- "google ads bureau anmeldelser"
- "google ads case studies"
- "bedste google ads bureau"

ACTION keywords:
- "book google ads konsultation"
- "få google ads tilbud"
- "google ads hjælp"
```

---

## Questions to Ask User

Use AskUserQuestion tool to gather constraints.

### Budget (with tier explanation)

"What's your monthly Google Ads budget?"
- Under 3,000 DKK → Micro tier (30-50 keywords max)
- 3,000-10,000 DKK → Lean tier (50-100 keywords)
- 10,000-30,000 DKK → Growth tier (100-200 keywords)
- Over 30,000 DKK → Scale tier (200+ keywords)

### Geographic Targeting

"Where do you want to show ads?"
- Single city (radius campaign)
- Multiple cities (geo-specific campaigns)
- Regional (e.g., Sjælland)
- National (full coverage)

### Language

"What language should ads be in?"
- Danish (language_id: 1009)
- Norwegian (language_id: 1012)
- Swedish (language_id: 1015)
- English (language_id: 1000)

### Conversion Goals

"What do you want people to do?"
- Fill out contact form
- Call phone number
- Book meeting
- Purchase product
- Download resource

### Competitors

"Who are your main competitors?"
- List 2-3 competitors for competitor campaign consideration
- Note if user wants to target competitor keywords

### Exclusions (CRITICAL)

"Is there anything we should NOT advertise?"
- Services not currently offered
- Geographic areas not served
- Customer types not wanted
- Products/services to exclude

---

## Common Patterns by Business Type

### Local Service
- Geographic modifiers critical ("flyttefirma københavn")
- "Near me" intent keywords
- Booking/quote intent ("få tilbud")
- Service area must match targeting

### E-commerce
- Product + category structure
- Price intent ("billig", "tilbud")
- Brand + product combinations
- Shopping campaigns primary

### B2B Services (Lead Gen)
- Industry-specific terminology
- Solution-focused keywords
- Longer decision cycles = educational content
- High CPC, lower volume

### Agency/Consultancy
- Service + outcome keywords
- Trust signals important
- Case studies drive conversions
- Multiple services = multiple campaigns

---

## Red Flags

Watch for these issues:

1. **No clear services page** - May need clarification from user
2. **Outdated website** - Verify services are still offered
3. **Multiple languages on site** - Confirm target language
4. **No contact form** - Conversion tracking may be difficult
5. **Conflicting messaging** - Ask user to clarify positioning
6. **No landing pages for services** - Discuss before proceeding
7. **B2B and B2C mixed** - Must split campaigns

---

## Output Template: `website_content.md`

```markdown
# Website Content: {Client Name}

## Business Type Classification

**Primary Type:** Lead Gen (B2B)

**Detection Signals:**
- Contact form as primary CTA (✓)
- Case studies section (✓)
- Services aimed at businesses (✓)

## Core Services

- **{Service 1}**: [Description, landing page URL]
- **{Service 2}**: [Description, landing page URL]

## Positioning

**Unique Differentiation:** [What makes them different]

**Key Tagline:** "[Primary messaging]"

## Target Customers

- **B2B/B2C:** B2B only
- **Industries:** [Target industries]
- **Geographic Focus:** [Denmark national / Copenhagen only / etc.]

## Unique Selling Points

- [USP 1]
- [USP 2]
- [USP 3]

## Buyer Journey Keywords (Per Service)

### Service 1: {Name}
- **Problem:** [keywords]
- **Solution:** [keywords]
- **Proof:** [keywords]
- **Action:** [keywords]

## Positioning → Keyword Translation ($POSITIONING_KEYWORDS)

**CRITICAL: This section is REQUIRED. It bridges positioning to keyword research.**

### Positioning Element 1: "[Tagline/differentiation]"

| Type | Keywords to Research |
|------|---------------------|
| Problem | [Pain points related to positioning] |
| Outcome | [Results the positioning promises] |
| Differentiation | [How positioning is expressed as keywords] |

### Positioning Element 2: "[Second positioning element]"

| Type | Keywords to Research |
|------|---------------------|
| Problem | [...] |
| Outcome | [...] |
| Differentiation | [...] |

## Landing Pages

| Service | URL | Has Form | Notes |
|---------|-----|----------|-------|
| Service 1 | /service-1/ | Yes | Ready |
| Service 2 | /service-2/ | Yes | Ready |

## Exclusions

- [What NOT to target]
- [Reason for exclusion]

## User Constraints

- **Budget:** [X DKK/month] (Tier: [Lean/Growth/Scale])
- **Geography:** [Target area]
- **Language:** [Danish] (ID: 1009)
- **Conversion Goal:** [Form fills / Calls / Bookings]
- **Competitors:** [List if provided]
```
