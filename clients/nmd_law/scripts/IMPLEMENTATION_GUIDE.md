# NMD Law Group - Complete Tracking Implementation Guide

## Current Situation

- **Website**: Wix (nmdlawgroup.com)
- **Forms**: GHL forms embedded as iframes
- **Problem**: GA4 shows 693 conversions, Google Ads shows 0 (broken import)
- **Facebook**: Already working (GHL has native Pixel field)
- **Google Ads**: No native GHL integration - needs custom solution

## Architecture

```
[User clicks Google Ad with GCLID] --> [Wix Landing Page]
                                              |
                    +-------------------------+-------------------------+
                    |                         |                         |
              [GTM on Wix]            [GHL Form iframe]           [GA4 on Wix]
              (stores GCLID)          (with our custom script)    (page views)
                    |                         |
                    +--- postMessage ---------+
                    (passes GCLID to iframe)  |
                                              |
                                        [Form Submit]
                                              |
                                              v
                                    [GHL stores lead + GCLID]
                                              |
                                              v
                                    [GHL Webhook fires]
                                              |
                                              v
                                        [n8n Workflow]
                                              |
                    +-------------------------+-------------------------+
                    |                                                   |
      [Google Ads Offline Conversion API]              [GA4 Measurement Protocol]
         (upload with GCLID)                             (generate_lead event)
```

## Step-by-Step Implementation

### Step 1: Create Google Ads Conversion Actions

Run the script to create conversion actions:

```bash
cd /Users/kaancatalkaya/Desktop/Projects/Google\ Ads\ -\ mondaybrew

# Activate virtual environment
source .venv-mcp/bin/activate

# Dry run first
python scripts/nmd_tracking/create_nmd_conversion_action.py --dry-run

# Create for real
python scripts/nmd_tracking/create_nmd_conversion_action.py
```

**SAVE THE OUTPUT** - You'll get:
- `LEAD_FORM_CONVERSION_ID`
- `QUALIFIED_LEAD_CONVERSION_ID`
- `PHONE_CLICK_CONVERSION_ID`

Update these in:
1. `config.py` - `conversion_actions` dict
2. `n8n_workflow_nmd_offline_conversions.json` - Replace placeholders

---

### Step 2: Add Tracking Script to GHL Form

1. **In GHL, edit the contact form** (Form ID: `s3tLhggeflPSsxlb2LCz`)

2. **Add a Hidden Field**:
   - Field Name: `gclid`
   - Field Type: Hidden
   - This will store the Google Click ID

3. **Add HTML Element**:
   - Drag an "HTML" element onto the form
   - Copy contents from `ghl_form_tracking_snippet.html`
   - Paste into the HTML element

4. **Save the form**

---

### Step 3: Add Parent Page Script to Wix

This enables GCLID communication between Wix and the GHL iframe.

1. Go to **Wix Dashboard** > **Settings** > **Advanced** > **Custom Code**

2. Add to **Header**:

```html
<script>
(function() {
  // Store GCLID when user lands from Google Ad
  var gclid = new URLSearchParams(window.location.search).get('gclid');
  if (gclid) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (90 * 24 * 60 * 60 * 1000));
    document.cookie = '_gclid=' + gclid + ';expires=' + expires.toUTCString() + ';path=/;SameSite=Lax';
    try { localStorage.setItem('_gclid', gclid); } catch(e) {}
  }

  // Listen for GCLID requests from GHL iframe
  window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'REQUEST_GCLID') {
      var storedGclid = new URLSearchParams(window.location.search).get('gclid');
      if (!storedGclid) {
        var match = document.cookie.match(/_gclid=([^;]+)/);
        storedGclid = match ? match[1] : localStorage.getItem('_gclid');
      }
      if (storedGclid && event.source) {
        event.source.postMessage({ type: 'GCLID_VALUE', gclid: storedGclid }, '*');
      }
    }
  });
})();
</script>
```

3. **Publish the site**

---

### Step 4: Set Up GHL Webhook to n8n

1. In GHL, go to **Settings** > **Webhooks**

2. Add webhook for **"Contact Created"**:
   - URL: `https://phpstack-1370137-5762452.cloudwaysapps.com/webhook/nmd-form-submission`
   - Events: Contact Created / Form Submission

3. Add webhook for **"Pipeline Stage Changed"** (for qualified leads):
   - URL: `https://phpstack-1370137-5762452.cloudwaysapps.com/webhook/nmd-pipeline-change`
   - Events: Opportunity Status Changed / Pipeline Stage Changed

---

### Step 5: Import n8n Workflow

1. Open n8n: https://phpstack-1370137-5762452.cloudwaysapps.com

2. Import `n8n_workflow_nmd_offline_conversions.json`

3. Configure credentials:
   - **Google Ads OAuth2**: Connect to MondayBrew MCC account
   - Environment variables needed:
     - `GOOGLE_ADS_DEVELOPER_TOKEN`
     - `GA4_API_SECRET` (from GA4 Admin > Data Streams > Measurement Protocol)

4. Update conversion action IDs in HTTP Request nodes:
   - Replace `LEAD_FORM_CONVERSION_ID` with actual ID
   - Replace `QUALIFIED_LEAD_CONVERSION_ID` with actual ID

5. **Activate the workflow**

---

### Step 6: Get GA4 Measurement Protocol Secret

1. Go to **GA4 Admin** (for G-GMJZFFYVF7)
2. **Data Streams** > Select stream
3. **Measurement Protocol API secrets**
4. Create new secret
5. Add to n8n as environment variable `GA4_API_SECRET`

---

### Step 7: Phone Call Tracking (Google Forwarding Numbers)

For phone call tracking, you have two options:

**Option A: Google Ads Call Extensions (Recommended)**
1. In Google Ads, go to **Ads & Extensions** > **Extensions**
2. Add **Call Extension**
3. Enter NMD's phone number
4. Enable **Call Reporting** - Google will use a forwarding number
5. Calls are automatically tracked as conversions

**Option B: Website Call Conversion (Advanced)**
1. In Google Ads, create a **Website Call Conversion**
2. You'll get a JavaScript snippet
3. Add to Wix via Custom Code
4. This dynamically swaps phone numbers for tracking

**Note**: On nmdlawgroup.com, the phone number is currently NOT a clickable `tel:` link. For best tracking, make it clickable:
```html
<a href="tel:+4512345678">+45 12 34 56 78</a>
```

---

## Testing Checklist

### Test GCLID Capture
1. Visit: `https://www.nmdlawgroup.com/contact?gclid=test12345`
2. Open browser DevTools > Application > Cookies
3. Verify `_gclid` cookie is set to `test12345`
4. Check the GHL form - hidden field should have GCLID value

### Test Form Submission
1. Submit a test form with GCLID in URL
2. Check GHL - new contact should have GCLID in custom field
3. Check n8n - webhook should trigger and show execution
4. Check n8n logs for Google Ads API response

### Test Google Ads Conversion
1. After form submit, check n8n execution for success
2. In Google Ads: **Tools** > **Conversions** > **Recent conversions**
3. Note: Can take up to 24 hours to appear

---

## Troubleshooting

### GCLID Not Captured
- Check browser console for errors
- Verify hidden field exists in GHL form
- Test postMessage by checking console for `[NMD Tracking]` logs

### n8n Webhook Not Receiving Data
- Verify webhook URL in GHL is correct
- Check n8n webhook is listening (test mode)
- Test with curl: `curl -X POST https://your-n8n-url/webhook/nmd-form-submission -d '{"test": true}'`

### Google Ads Shows Partial Failures
- Check GCLID format (should be ~100 chars)
- Verify conversion action ID is correct
- Check OAuth token hasn't expired

### Conversions Delayed
- Offline conversions can take 24-48 hours to appear
- Check Google Ads conversion reports for "pending" status

---

## Files Reference

| File | Purpose |
|------|---------|
| `config.py` | Central configuration (IDs, settings) |
| `create_nmd_conversion_action.py` | Creates Google Ads conversion actions |
| `setup_nmd_gtm.py` | Configures GTM (optional - for parent page) |
| `ghl_form_tracking_snippet.html` | JavaScript for GHL form |
| `n8n_workflow_nmd_offline_conversions.json` | n8n workflow definition |
| `README.md` | High-level overview |
| `IMPLEMENTATION_GUIDE.md` | This file - step-by-step guide |

---

## Maintenance

- **Weekly**: Check n8n execution logs for errors
- **Monthly**: Compare GHL leads vs Google Ads conversions
- **Quarterly**: Review conversion values, adjust if needed
- **On pipeline change**: Update qualified stages in n8n workflow

---

## IDs Quick Reference

| Service | ID |
|---------|-----|
| Google Ads Customer ID | `7562650658` |
| MondayBrew MCC | `8959543272` |
| GTM Container | `GTM-KZXHBNVN` |
| GA4 Measurement ID | `G-GMJZFFYVF7` |
| GHL Form ID | `s3tLhggeflPSsxlb2LCz` |
| Facebook Pixel ID | `1642362299753454` |
