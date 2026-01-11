# Negative Keyword Framework

Use this framework to generate the standard 3-layer negative keyword structure in Phase 3. **Negatives are as important as positive keywords.**

## Layer 1: Global Negatives (Universal)

Apply these to **ALL** campaigns (Lead Gen & E-com).

*   **Free/Cheap:** `free`, `gratis`, `cheap`, `billig`, `discount`, `tilbud` (unless discounter)
*   **Education/Career:** `job`, `career`, `karriere`, `salary`, `løn`, `internship`, `elev`, `training`, `course`, `education`, `university`, `skole`
*   **Do It Yourself:** `diy`, `how to`, `hvordan`, `selv`, `build`, `make`, `template`, `skabelon`
*   **Info/Research (Low Intent):** `what is`, `hvad er`, `definition`, `meaning`, `betydning`, `wiki`, `wikipedia`, `pdf`, `whitepaper`, `ebook`, `guide`, `statistics`, `statistikk`
*   **Media:** `image`, `photo`, `video`, `youtube`, `logo`, `icon`, `png`, `jpg`

## Layer 2: Vertical-Specific Negatives

Select the list matching the **Business Type** (Phase 1).

### For B2B / SaaS
*   `consumer`, `privat`, `home`, `hjem`, `personal`, `student`, `freelance`
*   (If high ticket): `small business`, `startup`, `mini`, `lite`

### For Local Service
*   `online`, `remote`, `virtual`
*   `parts`, `reservedele`, `supply`, `udstyr` (if only selling service)
*   `salary`, `løn` (competitors hiring)

### For E-commerce (High End)
*   `used`, `brugt`, `ebay`, `dban`, `marketplace`
*   `rental`, `leje` (if selling only)
*   `repair`, `reparation` (if selling new only)

## Layer 3: Strategic Control (Brand & Competitor)

### Brand Defencse
*   Add **[Client Brand Name]** as a negative phrase match to all **Non-Brand** campaigns.
*   *Why?* To force brand traffic into the cheap Brand campaign and keep Non-Brand CPA truthful.

### Competitor Protection
*   If **NOT** running a Competitor campaign:
    *   Add **[Top Competitors]** as negative phrase match to Non-Brand campaigns.
*   If **RUNNING** a Competitor campaign:
    *   Add **[Top Competitors]** as negative phrase match to Non-Brand campaigns (force traffic to Competitor campaign).

## Output Format

In `negative_keywords.json` or equivalent section, structure the output as:

```json
{
  "global_negatives": ["list", "of", "terms"],
  "vertical_negatives": ["list", "of", "terms"],
  "brand_negatives": ["brand name"],
  "competitor_negatives": ["comp1", "comp2"]
}
```
