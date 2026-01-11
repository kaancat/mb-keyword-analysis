---
name: warn-title-case-ad-copy
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: ad_copy\.json$
  - field: new_text
    operator: regex_match
    pattern: "Headline.{0,3}\":\s*\"[A-Z][a-z]+\s+[A-Z][a-z]+"
---

**Ad Copy Case Warning!**

Detected potential Title Case in headlines. Monday Brew uses **sentence case** for ad copy:

**Correct (sentence case):**
- "Professionel ørevoks fjernelse"
- "Book tid i Valby nu"

**Incorrect (title case):**
- "Professionel Ørevoks Fjernelse"
- "Book Tid I Valby Nu"

Only capitalize the first letter of the headline and proper nouns.
