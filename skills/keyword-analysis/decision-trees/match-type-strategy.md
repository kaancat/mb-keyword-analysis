# Match Type Strategy

Use this decision tree to assign match types in Phase 3. **Never default all keywords to one match type.**

## High-Level Rules

1.  **Budget Gate:** If Daily Budget < 50 DKK ($7/€7) -> **NO BROAD MATCH**.
2.  **Conversion Gate:** If expected conversions < 15/month -> **NO BROAD MATCH**.
3.  **Smart Bidding:** Broad match requires Smart Bidding (tCPA/tROAS). If using Manual CPC, stick to Phrase/Exact.

## Match Type Selection Logic

For each keyword theme, ask:

### 1. Is this a Brand or Competitor term?
*   **Yes:** Use **EXACT** Match.
    *   *Why?* You want total control over the message. You don't want "Nike" matching to "running shoes" broadly in a brand campaign.

### 2. Is this a High-Intent "Hero" term?
*(e.g., "emergency plumber", "buy running shoes", "software pricing")*
*   **Yes:** Use **EXACT** Match.
    *   *Bid Strategy:* Bid 20-30% higher than phrase equivalents.
    *   *Why?* We know this converts. We want to win the auction.

### 3. Is the budget "Micro" or "Lean"?
*   **Yes:** Use **PHRASE** Match (primary) and **EXACT** (top performers).
    *   *Why?* Broad match wastes too much spend on "learning" in small accounts.

### 4. Is the budget "Growth" or "Scale" AND we have >30 conv/month?
*   **Yes:** Can introduce **BROAD** Match.
    *   *Constraint:* Must be in a "Safety Net" structure or monitored closely.
    *   *Constraint:* Must have extensive Negative Keywords deployed first.

## Match Type Distribution Guidelines

| Budget Tier | Exact % | Phrase % | Broad % |
|-------------|---------|----------|---------|
| **Micro** | 80% | 20% | 0% |
| **Lean** | 40% | 60% | 0% |
| **Growth** | 30% | 50% | 20% |
| **Scale** | 30% | 40% | 30% |

## Formatting in Output

In `keyword_analysis.json`, the `match_type` field should reflect these decisions.

*   `"match_type": "exact"` for Brand/Competitor/Hero terms.
*   `"match_type": "phrase"` for Core exploration.
*   `"match_type": "broad"` ONLY if criteria met.

**Rationale Field:**
When adding a keyword, add a rationale note:
*   *"High intent hero term -> Exact"*
*   *"Core service exploration -> Phrase"*
*   *"Scale tier expansion -> Broad"*
