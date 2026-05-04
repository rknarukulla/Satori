# Skill: Stay Current — Docs & Warm-Up

This skill handles two distinct scenarios. Read the trigger carefully and follow only the matching flow.

---

## Scenario A — Setup Doc Fetch (user is configuring a platform)

**Trigger:** User says they want to add, set up, or configure a platform — OR a platform section is missing/placeholder in config.yaml and the user is asking about it.

**Goal:** Fetch the *current* official setup docs for that platform before walking the user through configuration. The static `docs/` files in this repo may be outdated — always confirm against live sources first.

**Rule:** Only fetch docs for the platform being set up. Do not fetch docs for other platforms.

### Fetch by platform

**Instagram / Meta:**
```
WebFetch: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/overview
WebSearch: "Meta Graph API Instagram long-lived token setup {current_year}"
```

**Google Play Store:**
```
WebFetch: https://developers.google.com/android-publisher/getting_started
WebSearch: "Google Play Developer API service account setup {current_year}"
```

**Apple App Store:**
```
WebFetch: https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests
WebSearch: "App Store Connect API key setup p8 {current_year}"
```

**LinkedIn:**
```
WebFetch: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api
WebSearch: "LinkedIn Pages API access token OAuth setup {current_year}"
```

After fetching, compare against the relevant `docs/{platform}-setup.md` file. If the live docs show a different step, UI label, or requirement, **follow the live version** — not the static file. Note any discrepancy to the user in one sentence.

Cache the result immediately (see Step 5 format below) so the session warm-up doesn't re-fetch it.

---

## Scenario B — Session Warm-Up (platforms are already configured)

**Trigger:** Session start, or user asks "has anything changed?", "are my docs current?", or a platform API returns an unexpected error.

**Goal:** Check if anything changed since the last fetch. Fast on repeat sessions — use cache aggressively.

### Step 1 — Determine which platforms to check

Read `config.yaml`. Only check platforms with non-placeholder values:

| Config field | Platform |
|---|---|
| `meta.token` not starting with `EAA_PASTE` | Instagram |
| `playstore.package_name` not `com.example` | Play Store |
| `appstore.key_id` not `XXXXXXXXXX` | App Store |
| `linkedin.access_token` not starting with `AQX_PASTE` | LinkedIn |

Tell the user: `"Warming up — checking {platform list}..."`

### Step 2 — Check cache per platform

For each platform, look for `data/platform-updates-{platform}-*.json` (platform = `instagram`, `playstore`, `appstore`, `linkedin`).

- **≤ 7 days old:** Read the cached summary. Mark ✓ — no fetch needed.
- **> 7 days old or missing:** Mark ⟳ — fetch needed.

If all platforms are cache-fresh, skip to Step 4 immediately. No fetches, no delay.

### Step 3 — Fetch changelogs only (for stale platforms)

Fetch **changelog/release notes pages only** — not full API docs. These are small, structured pages that summarise what changed. That's all that's needed to know if anything is different.

**Instagram:**
```
WebFetch: https://developers.facebook.com/docs/graph-api/changelog
WebFetch: https://developers.facebook.com/docs/instagram-platform/changelog
```

**Play Store:**
```
WebFetch: https://developers.google.com/android-publisher/release-notes
```

**App Store:**
```
WebFetch: https://developer.apple.com/documentation/appstoreconnectapi/app_store_connect_api_release_notes
```

**LinkedIn:**
```
WebFetch: https://learn.microsoft.com/en-us/linkedin/marketing/release-notes/
```

For each, extract only:
- Latest API version number (if versioned)
- Any deprecated endpoints that Satori uses
- Any new fields worth using
- Breaking changes to auth or scopes

Do **not** summarise the full changelog to the user — extract only what's actionable.

### Step 4 — Check algorithm / store signals (only if platform is in the current question)

Run WebSearch only for the platform the user is actively asking about — not all of them.

```
WebSearch: "{platform} algorithm update {current_month} {current_year}"
WebSearch: "{platform} ranking changes {current_year}"
```

Preferred sources: official newsrooms, platform developer blogs, Later/Hootsuite research. Skip SEO farms and unattributed posts.

**Skip this step** if the user's question is purely about data (e.g. "what are my impressions?") — algorithm research adds tokens with no benefit for a metrics lookup.

### Step 5 — Save cache (one file per platform, only if fetched)

```
data/platform-updates-{platform}-{YYYY-MM-DD}.json
```

Store only the synthesised summary — not raw fetched content:

```json
{
  "platform": "{name}",
  "checked_at": "{ISO timestamp}",
  "api_version_latest": "{version or null}",
  "deprecated_endpoints": [],
  "new_fields": [],
  "auth_changes": false,
  "algorithm_summary": "one sentence or null",
  "action_needed": false,
  "notes": "anything the user should know, or null"
}
```

### Step 6 — Report to user

Replace the "Warming up..." message with a single line.

**Nothing changed:**
> "Ready — {platform list} all current."

**Something changed on one platform:**
> "Ready. One note: {platform} {specific change in one sentence}. Adjusted for this session."

**Deprecated endpoint found:**
> "Ready. {Platform} deprecated [{endpoint}] — switching to the updated version automatically."

One or two sentences maximum. Do not summarise changelogs unprompted. The user came to analyse their metrics.

---

## What NOT to do

- **Don't fetch full API reference docs during warm-up** — changelogs only. Full docs are for setup (Scenario A).
- **Don't run algorithm search for platforms not in the current question** — waste of tokens.
- **Don't re-fetch if cache is under 7 days** — trust the cache.
- **Don't report "all clear" with a list of every platform checked** — if nothing changed, one line is enough.
- **Don't block the user's question** — if a fetch fails or times out, log it silently and proceed. Never make the user wait on a doc check.
