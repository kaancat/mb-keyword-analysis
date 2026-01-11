# Business Type Detection Framework

Use this decision tree to classify the client's business model based on website signals. This classification drives campaign strategy, keyword selection, and ad copy angles.

## Detection Logic

Analyze the website for the following signals. Count the matches to determine the primary business type.

| Business Type | Primary Signals (Strong) | Secondary Signals (Weak) | Campaign Strategy |
|---------------|--------------------------|--------------------------|-------------------|
| **Local Service** | • Visible physical address<br>• "Near me" keywords<br>• Service area map/list<br>• Local phone number | • "Emergency" or "Same day" language<br>• Service vehicle photos<br>• Local testimonials | **Hyper-Local:**<br>• Location-based keywords<br>• "Near me" modifiers<br>• Call-only ads / Call extensions<br>• Radius targeting |
| **E-commerce** | • "Add to cart" buttons<br>• Checkout flow<br>• Product catalog/SKUs<br>• Shipping info | • Product reviews<br>• "Sale" / "Offer" sections<br>• Inventory status | **Shopping-First:**<br>• Shopping / PMax feeds<br>• Category search campaigns<br>• Dynamic Remarketing<br>• ROAS bidding |
| **Lead Gen (B2B)** | • "Request Quote" / "Contact Us"<br>• Gatekeepers (Job title fields)<br>• Long forms | • Whitepapers / Ebooks<br>• Webinars<br>• "Enterprise" section | **Quality-Focused:**<br>• High-intent keywords<br>• "Service + for [Industry]"<br>• Manual CPC / tCPA with offline import<br>• Strict disqualification negatives |
| **SaaS** | • "Start Free Trial"<br>• Pricing tiers (Free/Pro/Ent)<br>• "Book Demo"<br>• Feature list | • API documentation<br>• Integrations page<br>• Case studies (Tech) | **Funnel-Based:**<br>• Competitor ("vs") campaigns<br>• Problem-solution keywords<br>• Brand defence<br>• Review sites Capterra/G2 |
| **Agency / Consultancy** | • "Book Meeting" / "Consultation"<br>• Case studies / Portfolio<br>• Team / About Us focus | • Methodology explanation<br>• Client logos<br>• Awards | **Authority-Based:**<br>• Service + Outcome keywords<br>• "Agency" / "Consultant" modifiers<br>• High-value remarketing<br>• tCPA (Booked Meeting) |

## Conflict Resolution

If a website shows signals for multiple types:

1.  **E-com vs Local:** If they sell products online BUT have a showroom -> Treat as **Hybrid**. Run Shopping for products, Local campaigns for store visits.
2.  **SaaS vs B2B:** If they have a "Demo" AND a "Trial" -> Treat as **SaaS** (usually more aggressive competitor bidding).
3.  **Local vs Lead Gen:** If they are a national service provider (e.g., nationwide plumbing chain) -> Treat as **Local** for campaign structure (city-levels) but **Lead Gen** for landing page strategy.

## Output Format

When reporting the detected business type in `website_content.md`, use this format:

```markdown
**Business Type:** [Type]
**Confidence:** [High/Medium/Low]
**Signals Found:**
- [Signal 1]
- [Signal 2]
**Implication:** [Brief strategy note, e.g., "Focus on location-based intent"]
```
