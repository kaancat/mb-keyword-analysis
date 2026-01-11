---
name: warn-all-phrase-match
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: keyword_analysis\.json$
  - field: new_text
    operator: not_contains
    pattern: Exact|exact
---

**Match Type Distribution Warning!**

All keywords appear to use Phrase match only. Per Monday Brew methodology:

| Budget Tier | Recommended Distribution |
|-------------|--------------------------|
| Micro (<3K DKK) | 80% Exact, 20% Phrase |
| Lean (3-10K DKK) | 40% Exact, 60% Phrase |
| Growth (10-30K DKK) | 30% Exact, 50% Phrase, 20% Broad |

Consider using Exact match for:
- Brand keywords (always Exact)
- High-value proven terms
- Competitor keywords
- Low-volume high-intent terms
