# Website Content: {Client Name}

## Business Type Classification

**Primary Type:** [Local Service / E-commerce / Lead Gen (B2B) / SaaS / Agency/Consultancy]

**Detection Signals:**
- [ ] [Signal 1]
- [ ] [Signal 2]
- [ ] [Signal 3]

**Positioning Mode:** [deep / standard]
- deep = Q11-Q13 were asked (consultant, coach, agency, SaaS)
- standard = Q11-Q13 skipped (commodity services, e-commerce)

---

## Canonical Service List ($CANONICAL_SERVICES) - REQUIRED

**Source:** Q9 (`$SERVICES_TO_ADVERTISE`) cross-referenced with website.

This is the SOURCE OF TRUTH for Phase 3 keyword validation.

| Service ID | Service Name | Landing Page | Keyword Variations | Included |
|------------|--------------|--------------|-------------------|----------|
| SVC-001 | [Service 1] | /path/ | [variations, aliases] | YES |
| SVC-002 | [Service 2] | /path/ | [variations, aliases] | YES |
| SVC-003 | [Service 3] | /path/ | [variations, aliases] | YES |

---

## Services NOT Offered ($SERVICES_NOT_OFFERED) - REQUIRED

**Source:** Q10 (`$SERVICES_NOT_TO_ADVERTISE`) + website analysis.

| Service | Source | Reason | Action in Phase 3 |
|---------|--------|--------|-------------------|
| [Service X] | Q10 | User said "don't advertise" | EXCLUDE keywords |
| [Service Y] | Website | No landing page | EXCLUDE keywords |
| [Service Z] | Analysis | Not mentioned in Q9 | EXCLUDE keywords |

---

## Core Services

For each service in `$CANONICAL_SERVICES`:

### {Service 1} (SVC-001)
- **Description:** [What is this service]
- **Target Market:** [Who buys this]
- **Landing Page:** [URL]
- **Conversion Action:** [Form / Call / Book]

### {Service 2} (SVC-002)
- **Description:** [What is this service]
- **Target Market:** [Who buys this]
- **Landing Page:** [URL]
- **Conversion Action:** [Form / Call / Book]

---

## Positioning (IF $POSITIONING_MODE = 'deep')

**Only complete this section if Q11-Q13 were asked.**

### Outcome Promise (from Q11: $OUTCOME_PROMISE)
> "[What outcome do you deliver - not tools, but results]"

### Positioning Language (from Q12: $POSITIONING_LANGUAGE)
> "[How do you describe what makes you different]"

### Client Pain Points (from Q13: $PAIN_POINTS)
> "[What frustration does your ideal client have before they find you]"

---

## Positioning → Keyword Translation ($POSITIONING_KEYWORDS)

**REQUIRED if $POSITIONING_MODE = 'deep'. Skip if 'standard'.**

For EACH positioning element, translate to keyword research seeds:

### Positioning Element 1: "[From Q12]"

| Type | Keywords to Research |
|------|---------------------|
| Problem | [Pain points related to positioning from Q13] |
| Outcome | [Results the positioning promises from Q11] |
| Differentiation | [How positioning is expressed as keywords] |

### Positioning Element 2: "[Second positioning element]"

| Type | Keywords to Research |
|------|---------------------|
| Problem | [...] |
| Outcome | [...] |
| Differentiation | [...] |

---

## Key Messaging

- **Primary Tagline:** "[Value proposition]"
- **Brand Voice:** [Formal / Casual / Technical / Accessible]
- **Emotional Appeal:** [Trust / Speed / Value / Quality / Innovation]

---

## Target Customers

- **B2B / B2C:** [Which]
- **Geographic Focus:** [Local / Regional / National / International]
- **Industries:** [If B2B, which industries]
- **Demographics:** [If B2C, age/interests/etc.]

---

## Unique Selling Points

- [USP 1: e.g., "Systems, not campaigns"]
- [USP 2: e.g., "Direct founder access"]
- [USP 3: e.g., "You own all data"]

---

## Landing Pages Audit

| Service | URL | Has Form | Has Phone | Status |
|---------|-----|----------|-----------|--------|
| [Service 1] | /path/ | Yes/No | Yes/No | Ready / Needs work |
| [Service 2] | /path/ | Yes/No | Yes/No | Ready / Needs work |

**Red Flag Check:** >50% of keywords landing on homepage? → STOP and discuss.

---

## Buyer Journey Mapping (Per Priority Service)

### {Service 1}

| Stage | Keywords to Research |
|-------|---------------------|
| PROBLEM | "why isn't X working", "struggling with Y" |
| SOLUTION | "X service", "X bureau" |
| PROOF | "X reviews", "best X" |
| ACTION | "book X", "get X quote" |

---

## User Constraints (from Phase 0)

- **Budget:** {$BUDGET} DKK/month (Tier: {$BUDGET_TIER})
- **Max Keywords:** {$MAX_KEYWORDS}
- **Max CPC:** {$MAX_CPC} DKK
- **Geography:** {Target area} (Location ID: XXXX)
- **Language:** {Danish/Norwegian/Swedish/English} (Language ID: XXXX)
- **Conversion Goal:** {$CONVERSION_GOAL}
- **History:** {$HISTORY}
- **Competitors:** {$COMPETITORS}

---

## Exclusions (from Q7 + Q10)

### Services NOT to Advertise ($SERVICES_NOT_TO_ADVERTISE)
- [From Q10 answers]

### Customer Types to Exclude
- [From Q7 answers - e.g., "B2C", "DIY seekers"]

### Geographic Exclusions
- [From Q7 answers - e.g., "Outside Denmark"]

---

## Navigation Structure

- /page-1/
- /page-2/
- /page-3/

---

## Additional Notes

[Any other relevant information: seasonal factors, current campaigns, competitor mentions, etc.]

---

## Phase 1 Checkpoint

- [ ] Website fetched and analyzed
- [ ] **Canonical Service List created** with Service IDs
- [ ] **Services NOT Offered documented**
- [ ] Business type validated
- [ ] Priority services have landing pages (or flagged)
- [ ] Buyer journey mapped (Problem → Solution → Proof → Action)
- [ ] **Positioning → Keyword translation completed** (if $POSITIONING_MODE = 'deep')

**If Canonical Service List is missing: DO NOT proceed to Phase 2.**
