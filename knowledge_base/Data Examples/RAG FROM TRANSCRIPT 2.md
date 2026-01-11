# Bulletproof Keyword Analyst AI — Strategic Extraction (Transcript Part 1)

Source: `Dokument2.docx` (meeting split into multiple parts). This file captures only the reusable strategy/process rules for Google Ads keyword analysis and structuring. More transcript parts can be appended as additional sections in this file or as separate `partN` files.

```json
{
  "match_type_philosophy": [
    "Default to phrase for reach on tight budgets; use exact on core/high-intent terms once volume supports control and lower CPC.",
    "Avoid broad in niche/local contexts to prevent irrelevant traffic; only consider after strong negatives and when scale is needed.",
    "Progression: start phrase → add exact for top converters → consider broad only with robust negatives and budget headroom."
  ],
  "ad_group_structure_logic": [
    "Begin consolidated when budget/volume are low; one core service ad group is fine.",
    "Split by intent/theme as data and budget grow: core service, destination variant, city/local variant, and brand.",
    "Give major cities or strong-performing clusters their own ad group; keep minor towns/low-volume variants grouped.",
    "Re-cluster existing accounts by performance clusters and align ad copy/landing pages per cluster."
  ],
  "keyword_research_process": [
    "Seed Keyword Planner with site URL for ideas, then rely on manual seed terms for relevance.",
    "Check avg monthly searches, 3-month/YoY change, competition, and top-of-page bid ranges; keep only terms with measurable volume.",
    "Translate core sets for other languages and re-check volume; drop synonyms with no data.",
    "Note cheaper variants (e.g., concatenated spellings) to lower CPC while staying relevant."
  ],
  "splitting_vs_consolidation_rules": [
    "Do not create ad groups for zero/negligible-volume terms; consolidate them.",
    "Split when a cluster has enough searches to support tailored ads/LPs and budget can fund learning.",
    "Keep low-volume variants consolidated to speed learning and avoid starving ad groups.",
    "Add a brand ad group when budget allows; otherwise keep in core if spend is very limited."
  ],
  "naming_conventions": [
    "Sheet columns: campaign, ad group, keyword, match type.",
    "Ad group names reflect theme/intent (e.g., Core-Wedding, Destination, City-Oslo, Brand)."
  ],
  "url_logic": [
    "Match landing page to ad group theme (destination page for destination terms, city page for city terms) to protect relevance/quality score."
  ],
  "category_specific_patterns": [
    "Wedding: Core Wedding Planning, Destination Wedding, City-specific (e.g., Wedding Planner Copenhagen/Oslo), Brand.",
    "Real estate/office rentals: major cities get their own groups; small towns stay grouped until volume justifies a split."
  ],
  "general_best_practices": [
    "Build and maintain negative keyword lists: exclude job seekers, DIY/how-to, unrelated event types, and off-geo locations; add cross-negatives between themes (e.g., exclude destination terms from local-only groups).",
    "Ad copy: mirror keyword and city/theme in headlines; use at least 2–3 responsive ad variants per ad group; pin one high-relevance headline; include a clear CTA; align copy with the landing page offer.",
    "Testing: rotate responsive ads, monitor top combinations, pause underperforming assets, and test one variable at a time (headline or description).",
    "Bidding & geo/device: keep bidding simple initially (manual eCPC or Max Clicks with cap) until conversions accumulate; target only serviceable geos; consider device bid adjustments after data (e.g., lower mobile if leads are weak).",
    "Decision to shift phrase → exact: when a phrase term has repeat conversions and enough volume for its own learning (e.g., consistent clicks and conversions weekly), add exact to control CPC and tighten intent; leave phrase running to retain reach.",
    "Use phrase match default on small budgets; add exact for top converters; avoid broad until negatives and budget maturity justify it.",
    "Brand campaigns are recommended even with low search volume—pay per click only and protect branded intent."
  ],
  "donot_include_or_irrelevant_topics": [
    "Budget amounts and daily spend math",
    "Forecasting formulas, CTR/CVR benchmarks from other channels",
    "Casual dialogue, spelling/language detours",
    "Unanswered or speculative questions",
    "Facebook performance references"
  ]
}
```

