# NMD Law Group - Server-Side Tracking Setup

Complete tracking implementation for NMD Law Group using GTM + n8n + Google Ads Offline Conversions.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────┘

[Google Ad] → User clicks → [NMD Website]
                                  │
                           ┌──────┴──────┐
                           │    GTM      │
                           │  (Browser)  │
                           └──────┬──────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
         [Captures]          [Fires to]          [Fires to]
              │                   │                   │
         • GCLID             GA4 Events         (Future: CAPI)
         • UTMs
         • Form data
              │
              ▼
    ┌─────────────────┐
    │   GHL Forms     │
    │  (with GCLID    │
    │  hidden field)  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   GHL CRM       │
    │  • Lead stored  │
    │  • GCLID saved  │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
[Form Webhook]   [Pipeline Webhook]
    │                 │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │      n8n        │
    │   Workflow      │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
[Google Ads      [GA4 Measurement
 Offline          Protocol]
 Conversions]
```

## Configuration IDs

| Service | ID |
|---------|-----|
| Google Ads Customer ID | `7562650658` |
| MondayBrew MCC | `8959543272` |
| GTM Container | `GTM-KZXHBNVN` |
| GA4 Measurement ID | `G-GMJZFFYVF7` |

## Setup Steps

### Step 1: Create Conversion Actions in Google Ads

```bash
cd /Users/kaancatalkaya/Desktop/Projects/Google\ Ads\ -\ mondaybrew

# Dry run first
python scripts/nmd_tracking/create_nmd_conversion_action.py --dry-run

# Create for real
python scripts/nmd_tracking/create_nmd_conversion_action.py
```

**Save the output!** You'll get conversion action IDs that need to be added to:
1. `config.py` - Update `conversion_actions` dict
2. `n8n_workflow_nmd_offline_conversions.json` - Replace `LEAD_FORM_CONVERSION_ID` and `QUALIFIED_LEAD_CONVERSION_ID`

### Step 2: Set up GTM Tags

```bash
# See current GTM configuration
python scripts/nmd_tracking/setup_nmd_gtm.py --dry-run

# Apply changes (but don't publish yet)
python scripts/nmd_tracking/setup_nmd_gtm.py

# After reviewing in GTM UI, publish
python scripts/nmd_tracking/setup_nmd_gtm.py --publish
```

This creates:
- **Variables**: GCLID (URL + Cookie), UTM params, Click URL, Form ID
- **Triggers**: All Pages, Phone Click, Form Submit, Window Loaded
- **Tags**: GA4 Config, GCLID Storage, Form Event, Phone Event

### Step 3: Configure GHL Forms

1. **Add hidden field for GCLID**:
   - In GHL, edit each form
   - Add a hidden field named `gclid`
   - The GTM tag will auto-populate this field

2. **Set up webhooks in GHL**:
   - Go to Settings → Webhooks
   - Add webhook for "Contact Created" → Point to n8n form webhook
   - Add webhook for "Pipeline Stage Changed" → Point to n8n pipeline webhook

### Step 4: Import n8n Workflow

1. Open n8n
2. Import `n8n_workflow_nmd_offline_conversions.json`
3. Configure credentials:
   - Create Google Ads OAuth2 credential
   - Set environment variables:
     - `GOOGLE_ADS_DEVELOPER_TOKEN`
     - `GA4_API_SECRET` (get from GA4 Admin → Data Streams → Measurement Protocol API secrets)
4. Update conversion action IDs in the HTTP Request nodes
5. Activate the workflow

### Step 5: Get GA4 API Secret

1. Go to GA4 Admin
2. Data Streams → Select your stream
3. Measurement Protocol API secrets
4. Create a new secret
5. Add to n8n environment variables as `GA4_API_SECRET`

### Step 6: Test the Flow

1. **Test GCLID capture**:
   - Visit site with `?gclid=test123`
   - Check cookie `_gclid` is set
   - Submit form, verify GCLID is captured

2. **Test n8n webhook**:
   - Use n8n's webhook test mode
   - Submit a test form in GHL
   - Verify data flows through

3. **Test Google Ads conversion**:
   - Check Google Ads → Conversions → Recent conversions
   - May take up to 24 hours to appear

## Files in This Directory

| File | Purpose |
|------|---------|
| `config.py` | Central configuration for all NMD IDs |
| `create_nmd_conversion_action.py` | Creates conversion actions in Google Ads |
| `setup_nmd_gtm.py` | Configures GTM with tracking tags |
| `n8n_workflow_nmd_offline_conversions.json` | Importable n8n workflow |
| `README.md` | This file |

## Conversion Flow

### Real-time (Form Submission)

```
Form Submit → GHL Webhook → n8n → Google Ads (with GCLID)
                                → GA4 (generate_lead event)
```

### Offline (Pipeline Change)

```
Lead Qualified in GHL → Webhook → n8n → Check if qualified stage
                                      → Google Ads Offline Conversion
                                      → GA4 (qualified_lead event)
```

## Troubleshooting

### GCLID not being captured

1. Check GTM Preview mode - is "Custom HTML - Store GCLID" firing?
2. Check browser cookies - is `_gclid` set?
3. Check GHL form - is hidden field present?

### n8n webhook not receiving data

1. Verify webhook URL in GHL
2. Check n8n execution logs
3. Test webhook URL directly with curl

### Conversions not appearing in Google Ads

1. Check n8n execution for errors
2. Verify conversion action ID is correct
3. Check Google Ads API response for partial failures
4. Note: Conversions can take up to 24 hours to appear

## Maintenance

- **Monthly**: Check conversion volume matches expected leads
- **Quarterly**: Review conversion values, adjust if needed
- **On pipeline change**: Update qualified stages in `config.py` and n8n workflow

## Support

Contact: MondayBrew
