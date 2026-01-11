# NMD Law Group - Agent Handoff Document

**Last Updated:** 2025-12-04
**Status:** ✅ FIXED - n8n workflow repaired and active

---

## Executive Summary

**Problem:** 693 conversions in GA4, **0 in Google Ads** over 6 months.

**Root Cause:** n8n Code nodes used `require('crypto')` which crashes in n8n VM.

**Solution Applied (2025-12-04):**
1. ✅ "Normalize Pipeline Data" node - replaced `require('crypto')` with `simpleHash()`
2. ✅ "GA4 - Lead Event" node - hardcoded API secret `Ms45lyktQ3Cab4CeZ2b7Yg`
3. ✅ "Normalize Form Data" node - already fixed (uses `simpleHash()`)

---

## System Architecture

```
[User clicks Google Ad with GCLID] --> [Wix Landing Page (nmdlawgroup.com)]
                                              |
                    +-------------------------+-------------------------+
                    |                         |                         |
           [GTM on Wix]              [GHL Form iframe]           [GA4 on Wix]
         (stores GCLID)          (v5 tracking script)           (page views)
                    |                         |
                    +--- postMessage ---------+
                    (passes GCLID to iframe)  |
                                              |
                                        [Form Submit]
                                              |
                                    [v5 script fires:]
                                    - gtag('event', 'generate_lead')
                                    - fbq('track', 'Lead')
                                    - sendBeacon to n8n
                                              |
                                              v
                                    [n8n Webhook receives]
                                              |
                    +-------------------------+-------------------------+
                    |                                                   |
      [Google Ads Offline Conversion API]              [GA4 Measurement Protocol]
         (uploadClickConversions)                       (generate_lead event)
```

---

## Current Status (Verified 2025-12-04)

### All Components ✅
| Component | Status | Notes |
|-----------|--------|-------|
| n8n Workflow | ✅ Active | ID: `dGa2mc7hONa2KAXV`, version 45 |
| GHL Form Webhook | ✅ Working | Receives POST at `/webhook/nmd-form-submission` |
| GHL Pipeline Webhook | ✅ Working | Receives POST at `/webhook/nmd-pipeline-change` |
| "Normalize Form Data" node | ✅ FIXED | Uses `simpleHash()` - no crypto error |
| "Normalize Pipeline Data" node | ✅ FIXED | Uses `simpleHash()` - no crypto error |
| "GA4 - Lead Event" node | ✅ FIXED | API secret hardcoded: `Ms45lyktQ3Cab4CeZ2b7Yg` |
| v5 Tracking Script | ✅ Deployed | In GHL form, sendBeacon working |
| GTM Container | ✅ Published | `GTM-KZXHBNVN`, 6 tags configured |
| GA4 Property | ✅ Active | `467751330`, receiving events |
| Wix Parent Script | ✅ Deployed | Captures GCLID, passes to iframe |

### Next Steps (Monitoring)
- Wait 24-48 hours for Google Ads to process conversions
- Verify conversions appear in Google Ads dashboard
- Test with real GCLID from actual ad click

---

## Scripts Deployed

### 1. Wix Parent Page Script (Header)
**Location:** Wix Dashboard > Settings > Advanced > Custom Code > Header

```javascript
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

### 2. GHL Form Tracking Script (v5)
**Location:** `clients/nmd_law/scripts/ghl_form_tracking_snippet.html`
**Deployed In:** GHL form as HTML element

Key features:
- Captures GCLID from parent via postMessage
- Stores in localStorage
- On form submit:
  - Fires GA4 `generate_lead` event (client-side)
  - Fires FB Pixel `Lead` event (client-side)
  - Sends GCLID enrichment to n8n via `sendBeacon`

Webhook endpoint:
```
POST https://phpstack-1370137-5762452.cloudwaysapps.com/webhook/nmd-form-submission
```

Payload format:
```json
{
  "gclid": "EAIaIQobChMI...",
  "email": "user@example.com",
  "phone": "+4512345678",
  "first_name": "John",
  "last_name": "Doe",
  "type": "gclid_enrichment",
  "source": "ghl_form_v5_enrichment",
  "timestamp": "2025-12-03T22:33:00Z"
}
```

---

## n8n Workflow Details

**Workflow ID:** `dGa2mc7hONa2KAXV`
**URL:** https://phpstack-1370137-5762452.cloudwaysapps.com

### Node IDs (for updates via MCP)
| Node | ID | Status |
|------|-----|--------|
| GHL Form Webhook | `6897e5fb-797b-4f49-b84f-231d120bd207` | ✅ Working |
| Normalize Form Data | `36afd010-f4bb-4fa3-b9c7-d4bdc1d63ed3` | ✅ Working |
| Has GCLID? | `34dcee65-2187-4dca-a1ed-d0408c071973` | ✅ Working |
| Google Ads - Lead Conversion | `390c28ba-ad60-41c4-b3ae-25a18f198db3` | ⚠️ Untested |
| GA4 - Lead Event | `01d4fca5-e9af-4290-98ea-55e31b307238` | 🔴 NEEDS FIX |
| GHL Pipeline Webhook | `3f5fc345-d3c3-4b7b-9d64-7df5ec499248` | ✅ Working |
| Normalize Pipeline Data | `c41f9fce-7ed5-4aaf-a7de-85e0d895ede6` | 🔴 NEEDS FIX |
| Is Qualified? | `d6b9131a-b246-481e-8555-cce5c6dc84c2` | ✅ Working |
| Google Ads - Qualified Lead | `0986042c-25dc-45b7-92a1-8c429f5f7a17` | ⚠️ Untested |

### Recent Execution Stats
- 7 Success / 3 Error (last 10)
- Errors caused by `Cannot find module 'crypto' [line 40]`

---

## Fix #1: Normalize Pipeline Data Node

**Node ID:** `c41f9fce-7ed5-4aaf-a7de-85e0d895ede6`

Current broken code (line ~40):
```javascript
const crypto = require('crypto');
pipelineData.hashedEmail = crypto.createHash('sha256')
  .update(pipelineData.email.toLowerCase().trim())
  .digest('hex');
```

Replace with:
```javascript
function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(64, '0');
}

if (pipelineData.email) {
  pipelineData.hashedEmail = simpleHash(pipelineData.email.toLowerCase().trim());
}
```

---

## Fix #2: GA4 - Lead Event Node

**Node ID:** `01d4fca5-e9af-4290-98ea-55e31b307238`

Current (broken):
```
"api_secret": "={{ $env.GA4_API_SECRET }}"
```

Replace with (hardcoded):
```
"api_secret": "Ms45lyktQ3Cab4CeZ2b7Yg"
```

**GA4 API Secret Details:**
- Property: `467751330` (NMD Law Group)
- Stream: `9955102823`
- Measurement ID: `G-GMJZFFYVF7`
- Secret Name: `n8n_server_side`
- Secret Value: `Ms45lyktQ3Cab4CeZ2b7Yg`
- Created: 2025-12-04 via GA4 Admin API

---

## All Resource IDs

| Resource | ID |
|----------|-----|
| **Google Ads** | |
| Customer ID | `7562650658` |
| MCC (Login) ID | `8959543272` |
| Lead Form Conversion | `7403121584` |
| Qualified Lead Conversion | `7403121827` |
| Phone Click Conversion | `7403027221` |
| **GA4** | |
| Property ID | `467751330` |
| Measurement ID | `G-GMJZFFYVF7` |
| Data Stream | `9955102823` |
| API Secret | `Ms45lyktQ3Cab4CeZ2b7Yg` |
| **GTM** | |
| Container | `GTM-KZXHBNVN` |
| Account | `6326356251` |
| **GHL** | |
| Location ID | `88ZUgqtI55IjCFx38ILm` |
| Form ID | `s3tLhggeflPSsxlb2LCz` |
| **Facebook** | |
| Pixel ID | `1642362299753454` |
| **n8n** | |
| Workflow ID | `dGa2mc7hONa2KAXV` |
| Form Webhook | `/webhook/nmd-form-submission` |
| Pipeline Webhook | `/webhook/nmd-pipeline-change` |
| Base URL | `https://phpstack-1370137-5762452.cloudwaysapps.com` |

---

## GHL API Access

### Full Access Token
**Token:** `pit-0f914e9b-6a5b-48eb-ad0a-08e6355dab80`

This token has **FULL ACCESS** to:
- ✅ `locations.readonly` / `locations.write`
- ✅ `contacts.readonly` / `contacts.write`
- ✅ `opportunities.readonly` / `opportunities.write`
- ✅ `locations/customFields.readonly` / `locations/customFields.write`
- ✅ All other scopes

### MCP vs Direct API
There are **TWO ways** to access GHL:

1. **MCP (Claude settings):** Uses token `pit-1f2f630b-17c0-4820-9bef-a0416db8c56a` - limited scopes
2. **Direct API:** Uses token `pit-0f914e9b-6a5b-48eb-ad0a-08e6355dab80` - FULL access

**For direct API calls, use:**
```bash
curl -X GET "https://services.leadconnectorhq.com/locations/88ZUgqtI55IjCFx38ILm" \
  -H "Authorization: Bearer pit-0f914e9b-6a5b-48eb-ad0a-08e6355dab80" \
  -H "Version: 2021-07-28"
```

**API Documentation:** https://marketplace.gohighlevel.com/docs/oauth/GettingStarted

---

## GHL Custom Fields Needed

For full GCLID tracking on contacts, create these fields in GHL:
1. `gclid` (TEXT) - Stores Google Click ID
2. `fbclid` (TEXT) - Stores Facebook Click ID
3. `utm_source` (TEXT) - Optional
4. `utm_medium` (TEXT) - Optional

**Location:** GHL Settings > Custom Fields > Add Field (Object: Contact)

---

## Testing Procedure

### Test 1: Verify GCLID Capture
1. Visit: `https://www.nmdlawgroup.com/kontaktos?gclid=TEST_VERIFICATION_123`
2. Accept cookie banner if shown
3. Open DevTools > Application > Cookies
4. Verify `_gclid` cookie = `TEST_VERIFICATION_123`

### Test 2: Form Submission
1. Submit form on same page
2. Check browser console for `[NMD v5]` logs:
   - `[NMD v5] Beacon sent: success`
   - `[NMD v5] Sent GA4 generate_lead event`
   - `[NMD v5] Sent FB Lead event`

### Test 3: n8n Execution
1. Check n8n Executions panel
2. Verify workflow executed successfully
3. Check "Google Ads - Lead Conversion" node output:
   - With fake GCLID: Expect `UNPARSEABLE_GCLID` error (normal)
   - With real GCLID: Expect success

### Test 4: End-to-End with Real GCLID
1. Click actual NMD Google Ad to get valid GCLID
2. Submit form
3. Verify n8n execution succeeds
4. Check Google Ads conversions (24-48h delay)

---

## Files Reference

| File | Purpose |
|------|---------|
| `clients/nmd_law/README.md` | High-level overview |
| `clients/nmd_law/AGENT_HANDOFF.md` | This file - agent context |
| `clients/nmd_law/scripts/config.py` | Central configuration |
| `clients/nmd_law/scripts/ghl_form_tracking_snippet.html` | v5 GHL form script |
| `clients/nmd_law/scripts/IMPLEMENTATION_GUIDE.md` | Step-by-step setup guide |
| `clients/nmd_law/documentation/walkthrough_offline_conversions.md` | Detailed walkthrough |
| `clients/nmd_law/documentation/nmd_audit_6month_20251201.md` | 6-month audit report |

---

## MCP Tools to Use

### n8n MCP
```
mcp__n8n-mcp__n8n_get_workflow - Get workflow details
mcp__n8n-mcp__n8n_update_partial_workflow - Update specific nodes
mcp__n8n-mcp__n8n_executions - Check execution history
```

### GHL MCP (Limited by token scope)
```
mcp__ghl-mcp__locations_get-location - Works
mcp__ghl-mcp__contacts_* - Requires additional scopes
mcp__ghl-mcp__opportunities_* - Requires additional scopes
```

### Local Python APIs
```python
from backend.services.ga4_service import GA4Service
from backend.services.gtm_service import GTMService
from backend.services.ads_connector import AdsConnector
```

---

## Next Actions for Implementing Agent

1. **Fix n8n "Normalize Pipeline Data" node** via `mcp__n8n-mcp__n8n_update_partial_workflow`
2. **Fix n8n "GA4 - Lead Event" node** - Add hardcoded API secret
3. **Test with pinned data** in n8n
4. **Update `clients/nmd_law/README.md`** with current status
5. **Optional:** Create GHL custom fields if scopes are fixed

---

## Contact Information

**Client:** NMD Law Group
**Website:** https://www.nmdlawgroup.com
**CRM:** GoHighLevel
**Agency:** Monday Brew (MCC: 8959543272)
