# NMD Law Group Conversion Tracking - Setup Guide

We have successfully configured the backend components for conversion tracking. Please follow these final manual steps to go live.

## 1. Google Tag Manager (GTM) Setup (Completed)
The GTM container has been fully configured and published.
*   **Status**: ✅ Published (Version 2 Live)
*   **Proof of Publish**:
    ![GTM Publish Success](/Users/kaancatalkaya/.gemini/antigravity/brain/dcae4537-e0dd-4800-9b46-7709349f8ec5/debug_gtm_publish_1764618403712.webp)

### What was done:
*   **Variables**: Enabled built-in `Form ID`, `Click URL` and created custom variables for GCLID/FBCLID.
*   **Triggers**: Added triggers for Page View, Form Submission, and Phone Clicks.
*   **Tags**: Configured GA4, FB Pixel, and the custom GCLID storage script.

## 2. GoHighLevel (GHL) Form Setup (Completed)
You have successfully implemented the "white and hidden" fields workaround.
*   **Status**: ✅ Done
*   **Action**: No further action needed on GHL side.

## 3. n8n Workflow Setup
The workflow is ready to be imported. It handles:
*   **Incoming Webhook**: Receives data from GHL.
*   **Normalization**: Cleans up phone numbers and hashes email/phone for Enhanced Conversions.
*   **Routing**: Sends "Form Submit" conversions to Google Ads and "generate_lead" events to GA4.
*   **Pipeline Changes**: Handles "Qualified Lead" offline conversions when status changes in GHL.

### Steps:
1.  **Import Workflow**:
    *   Download/Copy the workflow JSON: [n8n_workflow_nmd_offline_conversions.json](file:///Users/kaancatalkaya/Desktop/Projects/Google%20Ads%20-%20mondaybrew/scripts/nmd_tracking/n8n_workflow_nmd_offline_conversions.json)
    *   In n8n, click **Add Workflow** -> **Import from File** (or paste the JSON).
2.  **Configure Credentials**:
    *   **Google Ads**: Open the Google Ads nodes and select your OAuth2 credentials.
    *   **Google Analytics**: Open the GA4 nodes and select your credentials.
3.  **Set Environment Variables**:
    *   In n8n, go to **Settings** (or Variables).
    *   Add `GOOGLE_ADS_DEVELOPER_TOKEN` = `[Your Developer Token]` (I will provide this).
    *   Add `GA4_API_SECRET` = `[Your GA4 Secret]` (I will provide this).
4.  **Activate**:
    *   Toggle the workflow to **Active**.
4.  **Copy Webhook URLs**:
    *   Get the **Production URL** for the `GHL Form Webhook` node.
    *   Get the **Production URL** for the `GHL Pipeline Webhook` node.
    *   *You will need these to set up the Automation in GoHighLevel (Settings -> Automation).*

## 4. GoHighLevel (GHL) Setup
We need to prepare GHL to receive and send the tracking data.

### Step 4.1: Create Custom Fields
Before setting up automations, you must create the fields to store the IDs.
1.  Go to **Settings** -> **Custom Fields**.
2.  **Add Field** -> **Text** (Single Line).
    *   Name: `gclid`
    *   Object: Contact
3.  **Add Field** -> **Text** (Single Line).
    *   Name: `fbclid`
    *   Object: Contact

### Step 4.2: Automation Setup
Now we create the Automations to send data to n8n.

#### Automation 1: Form Submission -> n8n
1.  **Go to Automation** -> **Create Workflow** -> **Start from Scratch**.
2.  **Name**: "Google Ads - Form Submission Tracking".
3.  **Add Trigger**:
    *   Select **Form Submitted**.
    *   Add Filter: **Form is** -> Select your NMD Law Group form.
4.  **Add Action**:
    *   Select **Webhook**.
    *   **Method**: POST.
    *   **URL**: Copy and paste this **exact** URL:
        `https://phpstack-1370137-5762452.cloudwaysapps.com/webhook/nmd-form-submission`
        > [!TIP]
        > **Why was it showing 0.0.0.0?** n8n doesn't know its own public domain, so it shows `0.0.0.0` in the "Production URL" tab.
        > The trick is to take the **Test URL** (which has the correct domain) and simply remove `-test` from the path.
    *   **Custom Data**: Since GHL sends standard data (Name, Email, Phone) automatically, you only need to add our custom tracking IDs:
        | Key | Value (Select from Tag Icon -> Custom Fields) |
        | :--- | :--- |
        | `gclid` | `{{contact.gclid}}` |
        | `fbclid` | `{{contact.fbclid}}` |
    *   **Headers**: You can leave this **empty** (or default).
5.  **Publish**: Toggle to **Publish** and Save.

#### Automation 2: Pipeline Stage Change -> n8n
1.  **Go to Automation** -> **Create Workflow** -> **Start from Scratch**.
2.  **Name**: "Google Ads - Qualified Lead Tracking".
3.  **Add Trigger**:
    *   Select **Pipeline Stage Changed**.
    *   Add Filter: **Pipeline is** -> Select your NMD Pipeline.
    *   (Optional) Add Filter: **Stage is** -> Select specific "Qualified" stages if you want to limit it here (otherwise n8n handles it).
4.  **Add Action**:
    *   Select **Webhook**.
    *   **Method**: POST.
    *   **URL**: Copy and paste this **exact** URL:
        `https://phpstack-1370137-5762452.cloudwaysapps.com/webhook/nmd-pipeline-change`
    *   **Custom Data**: This is critical for tracking the **Value** ($$$).
        | Key | Value (Select from Tag Icon) |
        | :--- | :--- |
        | `monetaryValue` | `{{opportunity.value}}` |
        | `pipelineName` | `{{opportunity.pipeline}}` |
        | `stageName` | `{{opportunity.stage}}` |
        | `gclid` | `{{contact.gclid}}` |
5.  **Publish**: Toggle to **Publish** and Save.

## 5. Verification Checklist
Since I cannot access your browser's cookies or submit forms on your behalf, please perform these final checks:

1.  **Test GCLID Capture**:
    *   Visit `https://www.nmdlawgroup.com/kontaktos?gclid=TEST_GCLID_123`.
    *   **Important**: Click **"Accept"** (or "Godkend") on the Cookie Banner if it appears. The tracking script won't run without it!
    *   Open Developer Tools (F12) -> Application -> Cookies.
    *   **Verify**: Do you see a cookie named `_gclid` with value `TEST_GCLID_123`?
2.  **Test Form Submission**:
    *   Fill out the form on that same page.
    *   Submit it.
    *   **Verify**: Did you get a success message?
3.  **Check n8n**:
    *   Go to your n8n tab.
    *   Click **Executions** (left sidebar).
    *   **Verify**: Do you see a new successful execution? Click it to see if the data (including `gclid`) was sent to Google Ads.

## 6. Client Handoff & Explanation
Here is exactly what you need to tell the client and how to verify it works.

### How it Works (The "Magic")
1.  **Immediate Signal**: When a user submits a form, we immediately tell Google Ads "We got a Lead!".
2.  **Quality Signal**: When you (the client) talk to that lead and decide they are a good fit, you move them in GoHighLevel. We then tell Google Ads "That lead was **Qualified** (worth more money)!".
    *   *This teaches Google to find more "Qualified" people, not just "Form Fillers".*

### Instructions for the Client
"Just use GoHighLevel as normal. When a lead is good, make sure to move them to the **Qualified** stage in your pipeline. Our system handles the rest automatically."

### How it talks to Google Analytics (GA4)
You asked: *"How does this talk to Google Analytics?"*
**Answer**: It happens automatically in the background!
1.  **Form Submit**: When n8n receives the form, it sends a `generate_lead` event to GA4 with the GCLID.
2.  **Qualified Lead**: When you move the stage, n8n sends a `qualified_lead` event to GA4 with the **Value** you entered in the Opportunity.
    *   *This means you will see the actual Revenue in GA4!*

### How to Verify (In Google Ads)
1.  Go to **Google Ads** -> **Goals** -> **Conversions**.
2.  Look for the Conversion Action named **"Qualified Lead (Offline)"**.
3.  **Note**: It can take up to **24 hours** for offline conversions to appear in the chart.
4.  If you see numbers appearing there, the system is working perfectly!
