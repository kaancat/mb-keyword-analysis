---
name: require-roi-scenarios
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: roi_calculator\.json$
  - field: new_text
    operator: not_contains
    pattern: conservative|optimistic
---

**ROI Calculator Missing Scenarios!**

The ROI calculator should include three scenarios:
- **Conservative** (-30% conversion rate)
- **Expected** (baseline projection)
- **Optimistic** (+50% conversion rate)

This helps clients understand the range of possible outcomes.

Example structure:
```json
{
  "notes": {
    "scenarios": {
      "conservative": { "conversion_rate": 0.035, ... },
      "expected": { "conversion_rate": 0.05, ... },
      "optimistic": { "conversion_rate": 0.075, ... }
    }
  }
}
```
