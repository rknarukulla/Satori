# Play Store Setup — Google Play Developer API

This guide walks you through getting credentials so Satori can access your Play Store metrics.

**Time required:** ~15 minutes

---

## Step 1 — Enable the Android Publisher API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Go to **APIs & Services > Library**
4. Search for **"Google Play Android Developer API"**
5. Click it and press **Enable**

---

## Step 2 — Create a Service Account

1. In Google Cloud Console, go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g. `satori-playstore`) — the name is just for your reference
4. Skip the optional role and user access steps
5. Click **Done**
6. Find your new service account in the list, click it
7. Go to the **Keys** tab > **Add Key > Create new key**
8. Choose **JSON** format and click **Create**
9. A JSON file downloads automatically — **this is your key file (download only available once)**

---

## Step 3 — Grant the Service Account Access in Play Console

The service account exists in Google Cloud, but it also needs access in Play Console separately.

1. Go to [Google Play Console](https://play.google.com/console)
2. Click **Setup > API access** in the left sidebar
3. If prompted, link your Play Console account to a Google Cloud project (link the same project from Step 1)
4. Under **Service accounts**, you should see the account you just created — click **Grant access**
5. Choose the app(s) you want Satori to access (or grant account-level access)
6. For permissions, enable at minimum:
   - **View app information and download bulk reports** (required for app details and reviews)
   - **View financial data, orders, and cancellation survey responses** (required for vitals)
7. Click **Invite user** to save

---

## Step 4 — Add Credentials to Satori

1. Create a `credentials/` folder in your Satori directory (it's already gitignored):
   ```
   mkdir credentials
   ```
2. Move your downloaded JSON key file into it:
   ```
   mv ~/Downloads/your-key-file.json credentials/playstore-service-account.json
   ```
3. Open `config.yaml` and fill in the `playstore` section:
   ```yaml
   playstore:
     service_account_key_path: "credentials/playstore-service-account.json"
     package_name: "com.yourcompany.yourapp"
     app_name: "Your App Name"
   ```
   - `package_name` is found in Play Console under your app listing (e.g. `com.example.myapp`)

---

## Step 5 — Verify

Run the fetch script in Terminal from your Satori folder:

```
python fetch_playstore.py
```

A successful run looks like:
```
Satori — fetching your Play Store data

App: Your App Name (com.yourcompany.app)

  Authenticating with Google... OK

  Fetching app details... done
  Fetching reviews... 47 reviews
  Fetching crash rate... done
  Fetching ANR rate... done

✅  Done! Snapshot saved to data/snapshot-playstore-2026-05-03.json
```

If vitals show "skipped (Play Console vitals permissions not granted)", go back to Step 3 and ensure the financial data permission is enabled.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Google auth failed` | The Android Publisher API may not be enabled (Step 1), or the service account doesn't have Play Console access (Step 3) |
| `Service account key not found` | Check the path in `config.yaml` — run `ls credentials/` to verify the file is there |
| `package_name not found` | Double-check your package name against the Play Console URL: `play.google.com/console/u/0/developers/.../app/{packageName}` |
| Vitals always skipped | In Play Console > Setup > API access, ensure the service account has "View financial data" permission |
