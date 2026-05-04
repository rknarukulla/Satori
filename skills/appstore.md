# Satori — Apple App Store Skill

Load this file when the user asks about: App Store metrics, iOS performance, TestFlight, App Store reviews, Apple downloads, subscription revenue, or anything iOS/Apple-specific.

---

## Config Fields (read from config.yaml)

```
appstore.key_path       ← Path to .p8 EC private key file
appstore.key_id         ← 10-character Key ID from App Store Connect
appstore.issuer_id      ← UUID from App Store Connect
appstore.app_apple_id   ← Numeric Apple ID for the app (NOT the bundle ID)
appstore.vendor_number  ← Vendor number for sales/download reports
appstore.app_name       ← Display name for reports
```

---

## Data Mode Detection

**Check for a snapshot first:**
Look for the most recent file matching `data/snapshot-appstore-*.json`. Read it.
- If found and ≤ 7 days old: use it as the data source. Proceed normally.
- If found but > 7 days old: use it, but note at the start: *"Your App Store snapshot is from {date}. Run `python fetch_appstore.py` in Terminal to refresh it."*
- If not found: tell the user: *"I need you to run `python fetch_appstore.py` once in Terminal to pull your App Store data. Once done, come back and I'll have everything I need."*

**Direct HTTP mode** (ratings and reviews only — sales data always requires a snapshot):
Generate a JWT (see Auth section below) and fetch ratings/reviews directly. For download and revenue data, always ask for the snapshot — sales reports are gzip-compressed TSV files that can't be decoded via direct HTTP.

---

## Auth — App Store Connect JWT (direct mode only)

Apple requires a fresh JWT for every session (20-minute expiry — no refresh tokens).

**JWT structure (ES256 — ECDSA with P-256, NOT RSA):**
- Read `appstore.key_path` from config.yaml
- Read the `.p8` file at that path (PEM-encoded EC private key)
- Construct JWT with ES256:
  - Header: `{"alg": "ES256", "kid": "{key_id}", "typ": "JWT"}`
  - Payload:
    ```json
    {
      "iss": "{issuer_id}",
      "iat": {now},
      "exp": {now + 1200},
      "aud": "appstoreconnect-v1"
    }
    ```
  - Sign with the EC private key (ES256 / ECDSA + SHA256)
  - Encode all parts as base64url (no padding)

**Use Bearer token:**
All App Store Connect API calls: `Authorization: Bearer {signed_jwt}`

> Note: Apple's `.p8` keys use ECDSA (EC), not RSA. The signing algorithm is ES256, not RS256. This is the most common implementation error — double-check if auth fails.

---

## API Endpoints

Base URL: `https://api.appstoreconnect.apple.com/v1`

| Data | Endpoint |
|---|---|
| App info | `GET /apps/{appAppleId}?fields[apps]=name,bundleId,primaryLocale` |
| Customer reviews | `GET /apps/{appAppleId}/customerReviews?sort=-createdDate&limit=50` |
| Reviews — next page | Follow `links.next` URL from response |
| Sales reports | `GET /v1/salesReports?filter[frequency]=DAILY&filter[reportDate]={YYYY-MM-DD}&filter[reportType]=SALES&filter[vendorNumber]={vendor}&filter[reportSubType]=SUMMARY` |

**Sales reports:** Respond with `Accept: application/a-gzip`. The response body is a gzip-compressed TSV file. This cannot be decoded in direct mode — always use the snapshot for sales data.

**Pagination:** Reviews use cursor-based pagination via `links.next` in the response envelope.

---

## Derived Metrics

| Metric | How to compute |
|---|---|
| Downloads (30d) | Sum of `Units` from daily sales reports where `Product Type Identifier` is `1` (paid), `1F` (free), or `1T` (re-download) |
| Net revenue (30d) | Sum of `Developer Proceeds` from sales report rows |
| Avg daily downloads | Downloads (30d) / number of days with data |
| Review rating avg | Average of `attributes.rating` across fetched reviews |
| Review sentiment ratio | Count ratings 4–5 / total reviews |
| Recent vs. overall rating | Compare last 10 reviews vs. full snapshot average |

---

## Analysis Framing

Lead with the most actionable signal — in this order:
1. **Downloads trend** — daily download velocity and 30-day total; flag any sharp drops
2. **Store rating** — current average and recent trend (last 10 reviews vs. overall)
3. **Revenue / proceeds** — total and avg daily; flag if proceeds dropped while downloads held (price/IAP issue)
4. **Review sentiment** — surface themes from recent 1–2 star reviews first (most actionable)
5. **Review highlights** — pull 2–3 quotes from recent 5-star reviews for positive signal

App Store-specific context to include where relevant:
- **Ratings reset on major version updates** — note whether the current rating reflects only the current version. If the app had a recent major update, the current rating may not reflect historical quality.
- **App Store has a 48–72 hour data delay** — the most recent 2–3 days of sales data will be incomplete. Note this when discussing recent trends.
- **Negative reviews are indexed and searchable** — they directly impact conversion rate on the App Store product page. Responding via App Store Connect (Reviews tab) is visible to users.
- **App Store Connect requires a Finance role** for sales data and a Developer role for reviews/analytics. If certain data is missing, permissions may be the reason.

---

## Error Handling

| Error | Response |
|---|---|
| `.p8` key file not found | "I can't find the key file at `{path}`. Download it from App Store Connect > Users & Access > Integrations. Note: it can only be downloaded once — if lost, you'll need to revoke and create a new key. Update `appstore.key_path` in config.yaml." |
| JWT 401 | "App Store Connect JWT was rejected. Check that `appstore.key_id` and `appstore.issuer_id` in config.yaml match exactly what's shown in App Store Connect > Users & Access > Integrations. Also verify the `.p8` file hasn't been revoked." |
| API 403 on app | "Access denied for app ID `{app_apple_id}`. Verify your API key has the Developer or Finance role in App Store Connect > Users & Access > Integrations." |
| Sales report 404 | "No sales report found for that date. Reports can take 48–72 hours to generate. Try a date from 3+ days ago, or run `python fetch_appstore.py` which handles this automatically." |
| vendor_number missing | "Sales data requires `appstore.vendor_number` in config.yaml. Find it in App Store Connect > Payments and Financial Reports. I can still show ratings and reviews without it." |
| No snapshot and direct mode blocked | "Direct API calls aren't available here. Run `python fetch_appstore.py` in Terminal once and I'll read from the saved snapshot." |

---

## Snapshot Structure Reference

```json
{
  "fetched_at": "ISO timestamp",
  "platform": "appstore",
  "app": {
    "id": "123456789",
    "name": "App Name",
    "info": { "attributes": { "name": "App Name", "bundleId": "com.example.app" } }
  },
  "reviews": [
    {
      "id": "...",
      "attributes": {
        "rating": 5,
        "title": "Great app",
        "body": "...",
        "reviewerNickname": "...",
        "createdDate": "2026-01-15T12:00:00Z"
      }
    }
  ],
  "sales_30d": {
    "days": [ { "date": "YYYY-MM-DD", "units": 42, "proceeds": 18.50 } ],
    "total_downloads": 1200,
    "total_proceeds": 540.00,
    "pending_days": 2
  }
}
```
