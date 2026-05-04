# Satori — Google Play Store Skill

Load this file when the user asks about: Play Store metrics, Android performance, crash rate, ANR rate, Google Play reviews, app ratings, or anything Android-specific.

---

## Config Fields (read from config.yaml)

```
playstore.package_name              ← Android package name (e.g. com.yourcompany.app)
playstore.app_name                  ← Display name for reports
playstore.service_account_key_path  ← Path to service account JSON key file
```

---

## Data Mode Detection

**Check for a snapshot first:**
Look for the most recent file matching `data/snapshot-playstore-*.json`. Read it.
- If found and ≤ 7 days old: use it as the data source. Proceed normally.
- If found but > 7 days old: use it, but note at the start: *"Your Play Store snapshot is from {date}. Run `python fetch_playstore.py` in Terminal to refresh it."*
- If not found: tell the user: *"I need you to run `python fetch_playstore.py` once in Terminal to pull your Play Store data. Once done, come back and I'll have everything I need."*

**Direct HTTP mode** (when no snapshot exists and WebFetch is available):
Authenticate using the service account key (see Auth section below), then fetch live from the Play Developer API. Fall back to asking for the snapshot if auth fails.

---

## Auth — Service Account JWT (direct mode only)

To call the Play Developer API directly, generate a short-lived Bearer token:

**Step 1 — Build the JWT:**
- Read `playstore.service_account_key_path` from config.yaml
- Read the JSON key file at that path
- Extract: `client_email` (used as JWT `iss`) and `private_key` (RSA PEM key)
- Construct JWT with RS256:
  - Header: `{"alg": "RS256", "typ": "JWT"}`
  - Payload:
    ```json
    {
      "iss": "{client_email}",
      "scope": "https://www.googleapis.com/auth/androidpublisher",
      "aud": "https://oauth2.googleapis.com/token",
      "exp": {now + 3600},
      "iat": {now}
    }
    ```
  - Sign with the RSA private key (RS256 / PKCS1v15 + SHA256)
  - Encode all parts as base64url (no padding)

**Step 2 — Exchange for access token:**
```
POST https://oauth2.googleapis.com/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion={signed_jwt}
```
Response: `{ "access_token": "...", "expires_in": 3600 }`

**Step 3 — Use Bearer token:**
All Play Developer API calls: `Authorization: Bearer {access_token}`

---

## API Endpoints

Base URL: `https://androidpublisher.googleapis.com/androidpublisher/v3`

| Data | Endpoint |
|---|---|
| App details | `GET /applications/{packageName}/details` |
| Reviews | `GET /applications/{packageName}/reviews?maxResults=50&translationLanguage=en_US` |
| Reviews — next page | Add `&token={tokenPagination.nextPageToken}` |
| Crash rate clusters | `GET /vitals/crashrate/{packageName}/clusters` |
| ANR rate clusters | `GET /vitals/anrrate/{packageName}/clusters` |

**Pagination:** Reviews use `tokenPagination.nextPageToken` (not `cursor` or `after`).

**Vitals permissions:** The crash rate and ANR endpoints require "View app information and download bulk reports" permission in Play Console (Setup > API access). If they return 403, note it and work without vitals data.

---

## Derived Metrics

| Metric | How to compute |
|---|---|
| Store rating | `details.details.appDetails.rating` |
| Crash-free rate | `100 - crash_rate_percentage` from vitals clusters |
| Review sentiment ratio | Count ratings 4–5 / total reviews fetched |
| Recent review trend | Compare average rating of last 10 reviews vs. overall |

---

## Analysis Framing

Lead with the most actionable signal — in this order:
1. **Crash-free rate** — if < 99%, this is the top priority. A rate below 99% risks Play Store featuring removal.
2. **Store rating** — current rating and recent trend (last 10 reviews vs. overall)
3. **ANR rate** — often overlooked; high ANR rate is a leading indicator of churn
4. **Review sentiment** — surface themes from recent 1–2 star reviews first (most actionable)
5. **Review highlights** — pull 2–3 quotes from recent 5-star reviews for positive signal

Play Store-specific context to include where relevant:
- Ratings update slowly on Play Store — recent review text is a faster signal than the star average
- Google Play uses crash rate and ANR rate as ranking signals — these affect discoverability, not just stability
- Responding to reviews (especially negative ones) in Play Console improves conversion rate
- Rating doesn't reset on app updates (unlike App Store) — negative ratings persist until users re-rate

---

## Error Handling

| Error | Response |
|---|---|
| Service account key file not found | "I can't find the key file at `{path}`. Download it from Google Cloud Console and update `playstore.service_account_key_path` in config.yaml." |
| Auth 401 / token exchange failed | "Play Store auth failed. Check that the Android Publisher API is enabled in Google Cloud Console and that the service account has Play Console access (Setup > API access)." |
| API 403 on vitals | "Vitals data isn't accessible — your service account needs 'View app information' permission in Play Console (Setup > API access > grant access). I'll work with the data I have." |
| package_name missing | "I don't see a `playstore.package_name` in config.yaml. Add your app's package name (e.g. `com.yourcompany.app`) and try again." |
| No snapshot and direct mode blocked | "Direct API calls aren't available here. Run `python fetch_playstore.py` in Terminal once and I'll read from the saved snapshot." |

---

## Snapshot Structure Reference

```json
{
  "fetched_at": "ISO timestamp",
  "platform": "playstore",
  "app": { "packageName": "com.example.app", "name": "App Name" },
  "details": { "details": { "appDetails": { "rating": 4.2, "ratingCount": 1500 } } },
  "reviews": [
    {
      "reviewId": "...",
      "authorName": "...",
      "comments": [{ "userComment": { "starRating": 5, "text": "...", "lastModified": {} } }]
    }
  ],
  "vitals": {
    "crash_rate": { "metrics": [...] },
    "anr_rate": { "metrics": [...] }
  }
}
```
