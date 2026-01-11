# Phase 5: Ad Copy Reference

Detailed guide for persona-based RSA (Responsive Search Ad) creation.

---

## CRITICAL: Ad Group Differentiation

**The biggest mistake:** Using the same headlines across all ad groups.

The mondaybrew analysis had this problem: 4 ad groups, all with the same 6 headlines. Result: Generic, undifferentiated ads.

### The Rule

**Each ad group must have at least 3 UNIQUE headlines** not used in any other ad group.

### How to Differentiate

| Element | Same across ad groups | Unique per ad group |
|---------|----------------------|---------------------|
| H1 (DKI) | NO - fallback must be specific | YES |
| H2-H3 | NO - theme-specific benefits | YES |
| H4-H6 | OK if universal (trust, CTA) | Prefer unique |
| D1 | NO - describes specific service | YES |
| D2-D4 | OK if relevant to all | - |

### Example: mondaybrew (Correct)

**Ad Group: Google Ads**
```
H1: {KeyWord:Google Ads specialist}
H2: Flere leads, lavere CPC
H3: Data-drevet optimering
H4: Vi bygger systemer (shared)
H5: Book en gratis samtale (shared)
H6: 100+ B2B kunder (shared)

D1: Professionel Google Ads styring med fokus på leads, ikke klik. Vi optimerer løbende.
```

**Ad Group: CRM System**
```
H1: {KeyWord:CRM system til B2B}
H2: Al kundekontakt ét sted
H3: Aldrig tab et lead igen
H4: Vi bygger systemer (shared)
H5: Book en gratis samtale (shared)
H6: 100+ B2B kunder (shared)

D1: CRM system der samler alle leads og kunder. Integration med alle dine værktøjer.
```

**Ad Group: Hjemmesider**
```
H1: {KeyWord:B2B hjemmeside design}
H2: Konverterende design
H3: SEO-optimeret fra start
H4: Vi bygger systemer (shared)
H5: Book en gratis samtale (shared)
H6: 100+ B2B kunder (shared)

D1: Hjemmesider der konverterer besøgende til leads. Designet til B2B virksomheder.
```

### Validation Check

Before completing Phase 5, run this check:

```
For each ad group:
  unique_headlines = headlines NOT used in any other ad group
  if len(unique_headlines) < 3:
    FAIL - Rewrite to differentiate
```

---

## Persona-Based Copy Strategy

**Create ad copy aligned with buyer personas from Phase 2.**

### Persona → Copy Matrix

| Persona | H1 Focus | H2-H3 Focus | Descriptions |
|---------|----------|-------------|--------------|
| **High-Intent** | {KeyWord} + benefit | Urgency + proof | Process, speed, guarantee |
| **Research** | Category + differentiator | Value props | Why us, what's different |
| **Problem-Aware** | Pain acknowledgment | Solution teaser | Outcomes, easy start |

### High-Intent Persona Copy

**Mindset:** "I need this now"

```
Headlines:
H1: {KeyWord:Google ads bureau}  [pin 1]
H2: Få tilbud inden 24 timer
H3: Book en gratis samtale
H4: 100+ tilfredse kunder
H5: Certificerede specialister
H6: Start allerede i morgen

Descriptions:
D1: Professionel Google Ads styring. Book en gratis samtale og få en konkret plan.
D2: Vi hjælper B2B virksomheder med flere leads. Hurtig opstart og målbare resultater.
```

### Research Persona Copy

**Mindset:** "Which option is best?"

```
Headlines:
H1: {KeyWord:Google ads bureau}  [pin 1]
H2: Vi bygger systemer, ikke ads
H3: Fokus på leads, ikke klik
H4: Se vores resultater
H5: Anderledes tilgang
H6: Specialist i B2B

Descriptions:
D1: Vi fokuserer på systembaseret marketing, ikke tilfældige kampagner. Se hvorfor vi er anderledes.
D2: Gennemsigtighed og langsigtede resultater. Vi viser dig præcis hvad dine penge går til.
```

### Problem-Aware Persona Copy

**Mindset:** "I have a problem"

```
Headlines:
H1: Får du ikke nok leads?  [pain point]
H2: Der er en løsning
H3: Stop med at spilde penge
H4: Få et system der virker
H5: Fra kaos til kontrol
H6: Se forskellen

Descriptions:
D1: Mange virksomheder kæmper med uforudsigelige leads. Vi hjælper med at bygge et system.
D2: Stop med at gætte. Få en struktureret tilgang til marketing der faktisk virker.
```

---

## Headline Rules

### Character Limit
- **Maximum: 30 characters** per headline
- Include spaces in count
- Special characters count as 1

### Quantity
- **Minimum: 6 headlines** (Google requires)
- **Recommended: 8-10 headlines**
- **Maximum: 15 headlines** (don't pad with filler)

**Quality over quantity.** 8 strong headlines beat 15 weak ones.

### Case Rules

**USE SENTENCE CASE:**
```
✓ Kontor til leje i København
✓ Professionel erhvervsflytning
✓ Få et gratis tilbud i dag
```

**DO NOT USE TITLE CASE:**
```
✗ Kontor Til Leje I København
✗ Professionel Erhvervsflytning
✗ Få Et Gratis Tilbud I Dag
```

---

## Dynamic Keyword Insertion (DKI)

### Syntax
```
{KeyWord:fallback text}
```

### Case Options
- `KeyWord` = Capitalize first letter of each word
- `Keyword` = Capitalize first letter only (sentence case) ← RECOMMENDED
- `keyword` = All lowercase
- `KEYWORD` = All uppercase

### Placement
- **Always in Headline 1**
- **Always pin to position 1**

### Fallback Text Rules
- Must fit within 30 characters
- Should make sense if keyword doesn't match
- Should be specific to ad group theme

### Example
```
Headline 1: {KeyWord:Erhvervsflytning i København}
Headline 1 position: 1
```

If search query is "kontorflytning", ad shows:
> **Kontorflytning**

If keyword is too long, ad shows:
> **Erhvervsflytning i København**

---

## Location Insertion

### Syntax
```
{LOCATION(City):fallback}
```

### When to Use
- National campaigns targeting multiple cities
- Geo-targeted campaigns where city matters

### When NOT to Use
- Single-city campaigns (hardcode the city)
- Brand campaigns
- B2B where location is irrelevant

### Placement
- **Headline 2** (recommended)
- **Pin to position 2**

### Example
```
Headline 2: Kontorer i {LOCATION(City):din by}
Headline 2 position: 2
```

---

## USP to Headline Mapping (NEW)

For each USP from Phase 1, create TWO headline versions:

### Benefit Version (What they get)
### Proof Version (Why to believe)

**Example:**
```
USP: "Vi bygger systemer, ikke kampagner"

Benefit headline: "Få et system der virker"
Proof headline: "System-baseret tilgang"
```

**Example:**
```
USP: "20 års erfaring"

Benefit headline: "Erfarne specialister"
Proof headline: "Siden 2004 - 20+ år"
```

**Example:**
```
USP: "100% fokus på B2B"

Benefit headline: "Specialist i B2B"
Proof headline: "100+ B2B kunder"
```

---

## CTA Matching (NEW)

Match CTA to conversion goal from Phase 1.

| Conversion Goal | CTAs to Use |
|-----------------|-------------|
| Form fills | "Få tilbud", "Book en samtale", "Kontakt os" |
| Phone calls | "Ring nu", "Tal med os i dag" |
| Purchases | "Køb nu", "Bestil i dag" |
| Demos | "Se demo", "Prøv gratis" |
| Downloads | "Download guide", "Få vores tips" |

### Danish CTAs
```
Få et tilbud
Book en samtale
Kontakt os i dag
Ring nu
Se vores priser
Start i dag
Kom i gang
```

### Norwegian CTAs
```
Få et tilbud
Book en samtale
Kontakt oss i dag
Ring nå
Se våre priser
Start i dag
Kom i gang
```

---

## Position Pinning Rules

### When to Pin

| Position | Pin When | Example |
|----------|----------|---------|
| Position 1 | Using DKI | `{KeyWord:fallback}` |
| Position 2 | Using location insertion | `i {LOCATION(City):by}` |
| Position 2 | Critical brand message (brand campaigns) | "Spacefinder" |

### Leave Most Positions Blank

```
Headline 1: {KeyWord:Kontor til leje}
Headline 1 position: 1
Headline 2: Få tilbud i dag
Headline 2 position:          ← BLANK (let Google rotate)
Headline 3: Over 20 års erfaring
Headline 3 position:          ← BLANK
```

---

## Description Rules

### Character Limit
- **Maximum: 90 characters** per description

### Quantity
- **Exactly 4 descriptions** required

### Content Strategy

| Description | Focus | Example |
|-------------|-------|---------|
| D1 | Main value prop + CTA | "Professionel Google Ads styring. Book en gratis samtale i dag." |
| D2 | Key benefit or process | "Vi fokuserer på leads og kunder, ikke kun klik og impressions." |
| D3 | Trust/credibility | "100+ tilfredse B2B kunder. Certificerede Google Ads specialister." |
| D4 | Secondary benefit or offer | "Gennemsigtig rapportering og ingen binding. Start allerede i morgen." |

---

## Path Fields

### Rules
- **Path 1:** 15 characters max
- **Path 2:** 15 characters max
- Both appear in display URL: `example.dk/path1/path2`

### Best Practices
- Use keywords or service names
- Match landing page structure
- Keep short and readable

### Examples

| Service | Path 1 | Path 2 |
|---------|--------|--------|
| Google Ads | google-ads | bureau |
| CRM | crm | system |
| Websites | hjemmesider | design |
| Moving | erhverv | flytning |
| Office rental | kontorer | leje |

---

## Output Format

### `ad_copy.json`

```json
[
  {
    "Campaign": "mb | DA | Search | Google Ads",
    "Ad Group": "Google Ads Bureau | Danmark",
    "Persona Target": "High-intent",
    "Headline 1": "{KeyWord:Google ads bureau}",
    "Headline 1 position": "1",
    "Headline 2": "Få tilbud inden 24 timer",
    "Headline 2 position": "",
    "Headline 3": "Book en gratis samtale",
    "Headline 3 position": "",
    "Headline 4": "100+ tilfredse kunder",
    "Headline 4 position": "",
    "Headline 5": "Certificerede specialister",
    "Headline 5 position": "",
    "Headline 6": "Start allerede i morgen",
    "Headline 6 position": "",
    "Description 1": "Professionel Google Ads styring. Book en gratis samtale og få en konkret plan.",
    "Description 1 position": "",
    "Description 2": "Vi hjælper B2B virksomheder med flere leads. Hurtig opstart og målbare resultater.",
    "Description 2 position": "",
    "Description 3": "100+ tilfredse B2B kunder. Certificerede Google Ads specialister.",
    "Description 3 position": "",
    "Description 4": "Gennemsigtig rapportering og ingen binding. Start allerede i morgen.",
    "Description 4 position": "",
    "Path 1": "google-ads",
    "Path 2": "bureau",
    "Final URL": "https://mondaybrew.dk/google-ads/"
  }
]
```

### `ad_testing_plan.md` (NEW)

```markdown
# Ad Testing Plan: {Client Name}

## Testing Philosophy

- Test one element at a time
- Need 100+ clicks per variant for significance
- 2-4 week test periods minimum

## Planned Tests

### Test 1: CTA Urgency

**Ad Group:** Google Ads Bureau | Danmark
**Hypothesis:** Urgency-focused CTAs drive more conversions
**Variants:**
- A: "Få tilbud i dag"
- B: "Få tilbud inden 24 timer"
**Success Metric:** CTR > 5%

### Test 2: Benefit vs Proof

**Ad Group:** CRM System | Danmark
**Hypothesis:** Proof headlines build more trust
**Variants:**
- A: "Erfarne specialister" (benefit)
- B: "100+ tilfredse kunder" (proof)
**Success Metric:** Conversion rate

## Testing Schedule

| Week | Test | Ad Group |
|------|------|----------|
| 1-2 | Baseline | All |
| 3-4 | CTA Urgency | Google Ads |
| 5-6 | Benefit vs Proof | CRM |
```

---

## Quality Gate Checklist

Before proceeding to Phase 6, verify:

**DIFFERENTIATION (CRITICAL):**
- [ ] **Each ad group has at least 3 UNIQUE headlines** (not shared with other ad groups)
- [ ] **H1 fallback text is SPECIFIC to each ad group's theme**
- [ ] **D1 describes the SPECIFIC service of that ad group**

**FORMAT:**
- [ ] Sentence case applied (not Title Case)
- [ ] 6-10 headlines per ad group (quality over quantity)
- [ ] DKI in Headline 1 with position 1 pinning
- [ ] Location insertion in H2 for geo campaigns (pin position 2)
- [ ] 4 descriptions per ad group
- [ ] All URLs are specific landing pages
- [ ] Persona targeting documented per ad group
- [ ] USPs mapped to headlines (benefit + proof versions)
- [ ] CTAs match conversion goals

**If differentiation check fails: STOP. Rewrite ad groups with unique copy.**

---

## Common Mistakes

1. **Title Case** - "Få Et Tilbud I Dag" (should be "Få et tilbud i dag")
2. **15 padded headlines** - Weak headlines dilute strong ones
3. **Missing DKI** - Not using `{KeyWord:fallback}` in Headline 1
4. **Wrong pinning** - Pinning headlines that should rotate
5. **Generic fallbacks** - "Great Service" instead of specific benefit
6. **Too long** - Exceeding 30/90 character limits
7. **No CTAs** - Missing action-oriented headlines
8. **Homepage URLs** - Using homepage instead of specific landing pages
9. **No persona alignment** - Same copy for all searcher types
10. **No testing plan** - Not planning what to optimize
