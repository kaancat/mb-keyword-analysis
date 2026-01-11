# Campaign Split vs. Consolidate Logic

Use this framework in Phase 4 to determine the campaign structure. The modern Google Ads algorithm favors consolidation (more data), but business reality often requires segmentation (control).

## Default Starting State

Start with the simplest viable structure:
1.  **Brand Search** (Protect name)
2.  **Core Search** (Top priority services)

## When to SPLIT (Segmentation Rules)

Create a NEW campaign if:

### 1. Budget Control (The "Hog" Rule)
*   **Condition:** One service/theme consumes >60-70% of the budget, starving others.
*   **Action:** Move the "hog" to its own campaign with a dedicated budget cap.

### 2. Differing Goals
*   **Condition:** Service A needs Leads (CPA), Service B needs Awareness (Clicks).
*   **Action:** MUST split. You cannot mix bid strategies (tCPA vs Max Clicks) in one campaign.

### 3. Differing Economics
*   **Condition:** Service A is worth $10,000 (Consulting), Service B is worth $50 (E-book).
*   **Action:** MUST split. They need wildly different tCPA targets.

### 4. Geo / Language
*   **Condition:** Targeting multiple countries or languages.
*   **Action:** MUST split. `DK - English` and `DK - Danish` must be separate. `UK` and `US` must be separate.

### 5. Performance Divergence
*   **Condition:** A keyword theme has >30 conversions/month with a CVR 30% higher/lower than average.
*   **Action:** Split to maximize/protect its performance.

## When to CONSOLIDATE (Data Density Rules)

Merge campaigns if:

### 1. Data Starvation
*   **Condition:** Campaign has < 15 conversions/month.
*   **Action:** Merge with a similar theme. Smart Bidding fails without data points.

### 2. Budget Fragmentation
*   **Condition:** Campaign daily budget is < $10-20.
*   **Action:** Merge. You can't run a campaign on "coffee money".

### 3. Overlapping Intent
*   **Condition:** Keywords in Campaign A and Campaign B match the same search terms (Cannibalization).
*   **Action:** Merge and use Ad Groups to differentiate ad copy.

## Decision Matrix

| Scenario | Decision |
|----------|----------|
| New Account, Small Budget | **Consolidate** (Brand + 1 Core) |
| High Seasonality Difference | **Split** (Seasonal vs Evergreen) |
| B2B and B2C offerings | **Split** (Always) |
| Different Landing Page Domains | **Split** (Always) |

## Output Format

In `campaign_structure.json`, add a `rationale` field:

```json
{
  "campaign_name": "mb | DK | Search | Core Services",
  "rationale": "Consolidated core services due to Lean Budget (<10k). Split from Brand to protect CPA."
}
```
