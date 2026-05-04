# LinkedIn Setup — LinkedIn Pages API

This guide walks you through getting credentials so Satori can access your LinkedIn Company Page metrics.

**Time required:** ~10 minutes

**Note:** LinkedIn access tokens expire every 60 days. You'll need to refresh the token periodically — this guide covers that too.

---

## What You'll Collect

| Field | Where to find it | Example |
|---|---|---|
| Access Token | LinkedIn Developer Portal OAuth2 flow | `AQXxxxxxx...` |
| Org ID (numeric) | Your Company Page URL when in admin mode | `12345678` |

---

## Step 1 — Create a LinkedIn Developer App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Click **Create app**
3. Fill in:
   - **App name**: Satori (or any name)
   - **LinkedIn Page**: Select your Company Page
   - **App logo**: Upload any image (required)
4. Agree to the terms and click **Create app**

---

## Step 2 — Request Required OAuth Scopes

1. In your app, go to the **Products** tab
2. Request access to **Marketing Developer Platform**
   - This unlocks the `r_organization_social` and `rw_organization_admin` scopes needed for page analytics
   - Approval can take 1–3 business days for new apps
3. While waiting (or if you only need basic data), the **Sign In with LinkedIn using OpenID Connect** product gives you basic profile access immediately

> **Shortcut:** If your Company Page is small or you just need follower counts and posts, `r_organization_social` alone (available without Marketing Developer Platform) may be sufficient.

---

## Step 3 — Generate an Access Token

LinkedIn doesn't offer a simple token generator like Meta's Graph API Explorer. The easiest method for personal use:

### Option A — OAuth2 Token Generator (quickest)

1. In your app, go to the **Auth** tab
2. Under **OAuth 2.0 tools**, click **OAuth 2.0 token generator** (only available if you've added a product)
3. Select the scopes: `r_organization_social`, `rw_organization_admin`, `r_basicprofile`
4. Click **Request access token**
5. Authorize in the LinkedIn popup
6. Copy the generated access token

### Option B — Manual OAuth2 Flow

1. In your app's **Auth** tab, add `http://localhost:8000/callback` as an authorized redirect URL
2. Construct the authorization URL:
   ```
   https://www.linkedin.com/oauth/v2/authorization
     ?response_type=code
     &client_id={YOUR_CLIENT_ID}
     &redirect_uri=http://localhost:8000/callback
     &scope=r_organization_social%20rw_organization_admin%20r_basicprofile
   ```
3. Open that URL in a browser, authorize, and copy the `code` parameter from the redirect URL
4. Exchange the code for a token:
   ```
   POST https://www.linkedin.com/oauth/v2/accessToken
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code
   &code={CODE}
   &redirect_uri=http://localhost:8000/callback
   &client_id={YOUR_CLIENT_ID}
   &client_secret={YOUR_CLIENT_SECRET}
   ```
5. The response contains your `access_token`

---

## Step 4 — Find Your Company Page Numeric ID

The `org_id` is the numeric ID of your Company Page — **not** the vanity URL slug (e.g. `yourcompany`).

**Method 1 — Admin URL:**
1. Go to your Company Page on LinkedIn
2. Click **Admin tools** (top right)
3. Look at the URL — it will contain a numeric ID:
   `linkedin.com/company/12345678/admin/` → org_id is `12345678`

**Method 2 — API lookup:**
If you already have your token, run this in Terminal:
```
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organization~(id,name,vanityName)))"
```
The response shows all pages you administer with their numeric IDs.

---

## Step 5 — Add Credentials to Satori

Open `config.yaml` and fill in the `linkedin` section:

```yaml
linkedin:
  access_token: "AQXxxxxxxxxxxxxxxxxx"
  org_id: "12345678"
  org_name: "Your Company Name"
```

---

## Step 6 — Verify

Run the fetch script in Terminal from your Satori folder:

```
python fetch_linkedin.py
```

A successful run looks like:
```
Satori — fetching your LinkedIn data

Page: Your Company (org ID: 12345678)

  Fetching organization info... done
  Fetching follower statistics... done
  Fetching share/engagement statistics (last 30 days)... done
  Fetching recent posts... 18 posts
  Fetching stats for 18 posts... done

✅  Done! Snapshot saved to data/snapshot-linkedin-2026-05-03.json

   Your Company · 4,200 followers · 18 posts fetched
   28,400 impressions · 720 reactions (last 30 days)
```

---

## Refreshing the Token (every 60 days)

LinkedIn access tokens expire after 60 days. When Satori reports a 401 error:

1. Go back to the LinkedIn Developer Portal > your app > **Auth** tab
2. Use the OAuth2 token generator to generate a new token (same scopes)
3. Update `linkedin.access_token` in `config.yaml`
4. Re-run `python fetch_linkedin.py`

> **Tip:** Set a calendar reminder every 55 days to refresh before it expires.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `LinkedIn token expired or invalid (401)` | Generate a new token (Step 3) and update config.yaml |
| `HTTP 403 — missing permission` | Your app needs the Marketing Developer Platform product approved (Step 2). Check request status in the Products tab. |
| `Organization not found` | Double-check `linkedin.org_id` is the numeric ID, not the vanity slug. Use Method 2 in Step 4 to look it up via API. |
| No follower stats / empty response | Your token may lack `rw_organization_admin` scope. Regenerate with all scopes (Step 3). |
| Marketing Developer Platform pending | LinkedIn review takes 1–3 days. In the meantime, you can still get basic org info and posts with `r_organization_social`. |
