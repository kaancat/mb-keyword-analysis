# Discovery Brief: {Client Name}

**Date:** {Date}
**Prepared by:** Claude

---

## Phase 0: Discovery Questions (MANDATORY)

All questions must be answered before proceeding to Phase 1.

### Core Questions (Q1-Q8) - Always Ask

| # | Question | Variable | Answer |
|---|----------|----------|--------|
| Q1 | What does a typical customer spend? (First purchase or annual value) | `$CUSTOMER_VALUE` | |
| Q2 | Which 1-3 services should Google Ads focus on? | `$PRIORITY_SERVICES` | |
| Q3 | What's the monthly Google Ads budget? | `$BUDGET` | |
| Q4 | What counts as a successful conversion? (Form, call, purchase, demo) | `$CONVERSION_GOAL` | |
| Q5 | Have they run Google Ads before? What happened? | `$HISTORY` | |
| Q6 | Who do they actually lose customers to? | `$COMPETITORS` | |
| Q7 | Anything we should NOT target? (Services, locations, customer types) | `$EXCLUSIONS` | |
| Q8 | Any meeting notes, transcripts, or additional context? | `$ADDITIONAL_CONTEXT` | |

### Service Validation Questions (Q9-Q10) - MANDATORY

| # | Question | Variable | Answer |
|---|----------|----------|--------|
| Q9 | List ALL services to advertise via Google Ads. Be specific. | `$SERVICES_TO_ADVERTISE` | |
| Q10 | Any services you DON'T want to advertise, or that you DON'T offer? | `$SERVICES_NOT_TO_ADVERTISE` | |

### Positioning Questions (Q11-Q13) - CONDITIONAL

**Ask only if business type = consultant, coach, agency, SaaS, professional services**

| # | Question | Variable | Answer |
|---|----------|----------|--------|
| Q11 | What OUTCOME do you deliver? (Not tools, but results) | `$OUTCOME_PROMISE` | |
| Q12 | How do you describe what makes you different? | `$POSITIONING_LANGUAGE` | |
| Q13 | What frustration does your ideal client have before finding you? | `$PAIN_POINTS` | |

---

## Calculated Decisions

Based on answers above:

| Input | Calculation | Result |
|-------|-------------|--------|
| Budget: `$BUDGET` | Budget tier lookup | `$BUDGET_TIER` = |
| Budget tier | Max keywords lookup | `$MAX_KEYWORDS` = |
| Customer value: `$CUSTOMER_VALUE` | `Value × 5% × 20% ÷ 2.5` | `$MAX_CPC` = |
| Business type | Positioning mode | `$POSITIONING_MODE` = deep / standard |

---

## Canonical Service List (from Q9)

| Service ID | Service Name | Landing Page | Keyword Variations |
|------------|--------------|--------------|-------------------|
| SVC-001 | | | |
| SVC-002 | | | |
| SVC-003 | | | |

---

## Services NOT Offered (from Q10)

| Service | Reason | Action |
|---------|--------|--------|
| | | EXCLUDE keywords |
| | | EXCLUDE keywords |

---

## Strategic Direction

Based on discovery:

| Input | Decision |
|-------|----------|
| Budget: `$BUDGET` | **`$BUDGET_TIER` tier** → Max `$MAX_KEYWORDS` keywords |
| Customer value: `$CUSTOMER_VALUE` | **Max CPC target:** ~`$MAX_CPC` DKK |
| Priority services: `$PRIORITY_SERVICES` | **Campaigns:** [list] |
| Conversion goal: `$CONVERSION_GOAL` | **Bid strategy:** [strategy] |
| History: `$HISTORY` | **Watch out for:** [learnings] |

---

## RAG Insights

[Query RAG for methodology and present key insights here]

---

## Proposed Approach

1. **Campaign 1:** [purpose and focus]
2. **Campaign 2:** [purpose and focus]
3. **Brand campaign:** [if applicable]

---

## User Confirmation

**Does this strategic direction make sense before I proceed to Phase 1?**

- [ ] User confirmed approach
- [ ] Any adjustments noted

---

## Checkpoint: Phase 0 Complete

Before proceeding to Phase 1, verify:

- [ ] Q1-Q8 answered (core questions)
- [ ] Q9-Q10 answered (service validation - MANDATORY)
- [ ] Q11-Q13 answered IF complex service business (positioning)
- [ ] Budget tier calculated with keyword limits
- [ ] Max CPC calculated from customer value
- [ ] Canonical Service List documented
- [ ] Services NOT Offered documented
- [ ] RAG queried for methodology
- [ ] Strategic direction confirmed by user

**If any checkbox is incomplete: STOP. Do not proceed to Phase 1.**
