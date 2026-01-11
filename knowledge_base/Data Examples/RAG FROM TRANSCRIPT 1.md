# Bulletproof Keyword Analyst AI — Strategic Extraction (Mads del 1 + 2, merged)

Source: `/Users/kaancatalkaya/Downloads/Google Ads m. Mads del 1 + 2.docx` (merged meeting). Conversation includes a novice and an expert—only expert guidance retained.

```json
{
  "match_type_philosophy": [
    "Start with phrase to balance reach and relevance; layer in exact on top-converting queries once they show consistent volume to lower CPC and tighten intent.",
    "Avoid broad until the account has reliable signals (≈30–50+ conversions/month and strong negative lists); otherwise broad burns budget on loose matches.",
    "Decision path: launch phrase → add exact for winners → test broad only after data/negatives are strong and CPA is stable.",
    "Maintain and expand negatives (geo, jobs, DIY, information intent, off-category) so phrase/exact stay clean; mine search term reports weekly.",
    "Query hygiene: promote high-quality terms to exact, demote bad terms to negatives; this improves quality score and CPC over time."
  ],
  "ad_group_structure_logic": [
    "Structure by intent and controllables: product/category and location (city) so bids, copy, and LPs match user context.",
    "Early stage: one core search ad group per category; add city-specific ad groups only for high-priority or high-volume cities to avoid thin data.",
    "Always separate brand vs non-brand; run brand even at low volume to protect high-intent clicks.",
    "Display/YouTube: split prospecting and retargeting; for retargeting, segment by recency (e.g., 7d/30d/all-users) to manage reach vs frequency.",
    "If volume is very low for a product, keep one tight search ad group and shift incremental budget to awareness (display/YouTube) instead of over-splitting."
  ],
  "keyword_research_process": [
    "Discovery first: clarify products, objectives (awareness vs direct response), key SKUs, geos served, and landing pages available.",
    "Keyword Planner workflow: seed with core terms and competitor URLs; pull avg searches, 3m/YoY trend, competition, low/high top-of-page bids; export to sheet/plan.",
    "Prune zero or trace-volume terms; keep only synonyms with measurable volume; test concatenated spellings if CPC is lower and intent is intact.",
    "Localize: map synonyms and translations (e.g., Danish/English) and re-check volume before adding.",
    "Use ideation tools (ChatGPT, competitor SERP scans) only for brainstorming; always validate in Keyword Planner.",
    "Optional: create a Planner forecast (Plan → Forecast) for client expectations, then upload the curated keyword set back into campaigns."
  ],
  "splitting_vs_consolidation_rules": [
    "Avoid ad groups with no/trace volume—keep thin variants consolidated until data justifies a split.",
    "Split when a cluster (city/product/intent) shows sustained search volume or strategic importance and can support tailored ads/LPs.",
    "Graduate to broad only after strong data, negatives, and conversion volume; otherwise remain in phrase/exact.",
    "If demand is scarce, keep a tight search set and reallocate surplus budget to awareness formats rather than over-fragmenting search."
  ],
  "naming_conventions": [
    "Campaign naming pattern: Provider/Brand – Country – Channel – Goal/Product (e.g., DK-Search-StickyMat, DK-Display-BrandAwareness).",
    "Ad groups named by theme: Product (StickyMat), Location (København), Brand, Prospecting, Retargeting-30d, Retargeting-AllUsers.",
    "Maintain sheet columns: Campaign, Ad Group, Keyword, Match Type, Notes (intent/volume), Landing Page."
  ],
  "url_logic": [
    "Send traffic to the most specific relevant LP: city page for city ad group, product page for product terms; avoid generic LPs for localized ads.",
    "Apply global gtag via GTM; set conversion tracking on key actions; prefer server-side or element-level tags for reliability."
  ],
  "category_specific_patterns": [
    "Office hotels/commercial space: ad groups by major cities; heavy negative geo list for cities not served; display remarketing to site visitors.",
    "Low-volume B2B products (e.g., protective mats): few core search terms; consider single search ad group + awareness/display to generate demand.",
    "YouTube/Display: prospecting audiences by in-market/affinity; retargeting audiences built from site visitors (multiple lookback windows)."
  ],
  "general_best_practices": [
    "Use MCC/manager accounts for multi-client oversight; keep account structure consistent for quick audits.",
    "Segment placements: Search for intent; Display/YouTube mainly for remarketing and light prospecting; skip Maps/Gmail when user behavior doesn’t fit category.",
    "Responsive display/video: upload all requested sizes (landscape/square/portrait); Google auto-fits; use HTML5 if richer motion is needed.",
    "Display setup (remarketing): create campaign → display → set geo/ language → audiences: add All Users 7d/30d/All Time; upload images; add 3–5 headlines + descriptions; set frequency guardrails via observation; monitor impressions/user and tighten windows if high.",
    "Audience templates: prospecting via in-market/affinity for the category; retargeting via site visitors with multiple lookback windows; optionally stack similar audiences if size is low.",
    "Negative keyword lists: include off-geo locations, job seekers (job, salary, career), DIY/how-to, free/cheap terms, unrelated verticals, competitor cities you do not serve; add cross-negatives between themes (e.g., exclude destination terms from local-only groups).",
    "Bidding/geo/device: start simple (Max Clicks with CPC cap or eCPC) until conversions accrue; target only serviceable geos; apply device bid adjustments after data (e.g., reduce mobile if lead quality is weak).",
    "Tracking: place global gtag via GTM; define conversions on key actions (form submit/call/button); verify firing; prefer server-side or element-level tagging where possible.",
    "Search term hygiene: weekly SQRs; add winners as exact, add losers as negatives; update shared negative lists across campaigns.",
    "Remarketing frequency: watch impressions/user; widen lookback if spend is too low; narrow or cap if frequency is excessive without clicks.",
    "When expanding markets: replicate naming pattern (Country → Channel → Goal/Product) and reuse negative lists/structures for consistency and speed."
  ],
  "donot_include_or_irrelevant_topics": [
    "Casual chit-chat, complaints about cold office, lunch plans",
    "Budget amounts or daily spend math",
    "User confusion about interfaces or keyboard shortcuts",
    "Speculative statements from the novice participant",
    "Non-strategic tool navigation chatter"
  ]
}
```
