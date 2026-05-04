# App Store Setup — App Store Connect API

This guide walks you through getting credentials so Satori can access your App Store metrics.

**Time required:** ~10 minutes

---

## What You'll Collect

| Field | Where to find it | Example |
|---|---|---|
| Key ID | App Store Connect > Users & Access > Integrations | `ABC123DEF4` |
| Issuer ID | Same page, shown at the top | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| .p8 private key | Downloaded when you create the key | `AuthKey_ABC123DEF4.p8` |
| Apple ID (numeric) | App Store Connect > My Apps > App Information | `1234567890` |
| Vendor Number | App Store Connect > Payments and Financial Reports | `87654321` |

---

## Step 1 — Create an API Key

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Click **Users and Access** in the top navigation
3. Select the **Integrations** tab
4. Under **App Store Connect API**, click the **+** button to create a new key
5. Give it a name (e.g. `Satori`) and choose a role:
   - **Developer** — gives access to app info and reviews
   - **Finance** — required for sales/download reports and revenue data
   - If you want both reviews and download data, choose **Finance** (it includes developer access)
6. Click **Generate**

---

## Step 2 — Download Your Key

After creating the key:

1. **Download the .p8 file immediately** — this is the only time you can download it. If you miss it, you'll need to revoke the key and create a new one.
2. Note the **Key ID** (shown in the key list — 10 characters)
3. Note the **Issuer ID** (shown at the top of the Integrations page)

---

## Step 3 — Find Your Apple ID and Vendor Number

**Apple ID (numeric):**
1. In App Store Connect, go to **My Apps**
2. Select your app
3. Click **App Information** in the left sidebar
4. Find **Apple ID** — it's a plain number like `1234567890`
5. This is different from your bundle ID (`com.yourcompany.app`) — Satori needs the numeric Apple ID

**Vendor Number:**
1. In App Store Connect, go to **Payments and Financial Reports**
2. Your Vendor Number is shown in the top-left corner of that page
3. It's also in any downloaded financial report filenames

---

## Step 4 — Add Credentials to Satori

1. Create a `credentials/` folder in your Satori directory (it's already gitignored):
   ```
   mkdir credentials
   ```
2. Move your downloaded .p8 key file into it:
   ```
   mv ~/Downloads/AuthKey_XXXXXXXXXX.p8 credentials/appstore-key.p8
   ```
3. Open `config.yaml` and fill in the `appstore` section:
   ```yaml
   appstore:
     key_path: "credentials/appstore-key.p8"
     key_id: "XXXXXXXXXX"
     issuer_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     app_apple_id: "1234567890"
     vendor_number: "87654321"
     app_name: "Your App Name"
   ```

---

## Step 5 — Verify

Run the fetch script in Terminal from your Satori folder:

```
python fetch_appstore.py
```

A successful run looks like:
```
Satori — fetching your App Store data

App: Your App Name (Apple ID: 1234567890)

  Generating App Store Connect JWT... OK

  Fetching app info... done
  Fetching App Store reviews... 38 reviews
  Fetching sales reports (last 30 days)...
    10/30 days processed...
    20/30 days processed...
    30/30 days processed...
  Sales done — 1,247 downloads · $498.00 proceeds (2 days pending — App Store reports have a 48h delay)

✅  Done! Snapshot saved to data/snapshot-appstore-2026-05-03.json

   Your App Name · 38 reviews fetched · 1,247 downloads · $498.00 proceeds (30d)
```

The "days pending" note is normal — App Store Connect has a 48–72 hour delay on report generation.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `App Store Connect JWT was rejected` | Check that `key_id` and `issuer_id` in config.yaml match exactly what's shown in App Store Connect. Both are case-sensitive. |
| `.p8 key file not found` | Verify the path with `ls credentials/`. If the file is missing entirely, you'll need to revoke the key in App Store Connect and create a new one — `.p8` files can only be downloaded once. |
| `Access denied for app_apple_id` | Your API key's role may be too restrictive. Finance role is needed for sales data; Developer role for reviews. |
| Sales report returns 404 | Reports aren't ready yet — Apple has a 48–72h delay. Try running the script the next day, or it will skip those days automatically. |
| `vendor_number missing` | The vendor number is only needed for sales data. If you just want reviews and ratings, you can leave it blank — Satori will skip sales reports. |
