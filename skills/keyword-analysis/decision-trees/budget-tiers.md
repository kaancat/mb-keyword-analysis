# Budget Tier & Keyword Limits

Use this framework to determine the account size tier and enforce strict keyword limits. The #1 mistake is adding too many keywords for the budget,diluting spend and preventing optimization.

## 1. Determine Budget Tier

Convert the monthly budget to the target market currency (DKK, NOK, SEK, EUR, USD).

| Budget (Monthly) | Tier Name | Characteristics |
|------------------|-----------|-----------------|
| **< 3,000 DKK**<br>(< $450 / €400) | **Micro** | Survival mode. Cannot afford waste. Must be ruthless with intent. |
| **3,000 - 10,000 DKK**<br>($450 - $1.5k / €400 - €1.3k) | **Lean** | Building foundation. Focus on core services and proven intent. |
| **10,000 - 30,000 DKK**<br>($1.5k - $4.5k / €1.3k - €4k) | **Growth** | Expansion mode. Can afford some testing and broader reach. |
| **> 30,000 DKK**<br>(> $4.5k / €4k ) | **Scale** | Market domination. Full funnel coverage including awareness. |

## 2. Enforce Keyword Limits

Based on the tier, apply these HARD limits to Phase 3 (Keyword Research).

| Tier | Max Total Keywords | Max Campaigns | Match Type Bias | Focus Area |
|------|--------------------|---------------|-----------------|------------|
| **Micro** | **30 - 50** | **1 + Brand** | **80% Exact**<br>20% Phrase<br>0% Broad | Only the single highest-margin service. No "research" intent. |
| **Lean** | **50 - 100** | **2 - 3 + Brand** | **60% Phrase**<br>40% Exact<br>0% Broad | Core services. Main problem/solution keywords. |
| **Growth** | **100 - 200** | **Full Coverage** | **50% Phrase**<br>30% Exact<br>20% Broad | All services. Competitor campaigns. Broader problems. |
| **Scale** | **200+** | **Segmented** | **40% Phrase**<br>30% Broad<br>30% Exact | Full funnel. Geo-splits. Niche personas. |

## 3. The "Max Clicks" Verification

Before finalizing the keyword list, run this math:

1.  **Daily Budget** = Monthly Budget / 30.4
2.  **Est. CPC** = (Get from RAG or benchmarks)
3.  **Max Daily Clicks** = Daily Budget / Est. CPC

**Rule:** If `Max Daily Clicks` < 10, you CANNOT trigger Smart Bidding efficiently.
*   **Action:** Reduce active keywords to top 5-10 Exact Match "Heroes" only.
*   **Action:** Consolidate all non-brand into 1 campaign.

## Output

In `discovery_brief.md`, clearly state:

```markdown
**Budget Tier:** [Tier]
**Keyword Limit:** [Max]
**Rationale:** "With a budget of [X], we can generate approx [Y] clicks/day. To ensure data density for optimization, we must limit active keywords to [Max]."
```
