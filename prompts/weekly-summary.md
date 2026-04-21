# Prompt: Weekly Account Summary

Use this prompt every Monday (or whenever the user asks for a weekly review).

---

## Instructions for Claude

Execute the following steps in order:

### 1. Define the time window
- `since` = 7 days ago (Unix timestamp)
- `until` = today (Unix timestamp)

### 2. Fetch account-level insights
```
GET /{account_id}/insights
  ?metric=reach,impressions,profile_views,follower_count
  &period=day
  &since={since}
  &until={until}
  &access_token={token}
```
Extract: total reach, total impressions, profile views, follower delta (end minus start).

### 3. Fetch posts from the past 7 days
```
GET /{account_id}/media
  ?fields=id,caption,media_type,timestamp,like_count,comments_count,permalink,thumbnail_url,media_url
  &limit=30
  &access_token={token}
```
Filter results to only posts where `timestamp` falls within the 7-day window.

### 4. Fetch per-post insights for each filtered post
```
GET /{media_id}/insights
  ?metric=reach,impressions,saved,shares,engagement
  &access_token={token}
```
Build a list: `[{ id, media_type, timestamp, reach, saves, engagement, like_count, comments_count }]`

### 5. Compute summary metrics
- **Best post**: highest saves
- **Worst post**: lowest reach
- **Avg engagement rate**: (total likes + comments + saves) / total reach × 100
- **Top media type**: which type (REEL, CAROUSEL_ALBUM, IMAGE) had highest avg reach
- **Follower growth**: net change this week vs last week (if prior snapshot available in `data/`)

### 6. Run Llama analysis (if llama_api_key is set)
Send the full metric list to Llama 3.3-70B with the prompt:
> "These are Instagram metrics for a 7-day period. Identify the most important pattern, anomaly, or opportunity in 3–5 sentences. Be specific and actionable."

### 7. Write data snapshot
Save raw data to `data/snapshot-{YYYY-MM-DD}.json`.

### 8. Generate response
Output in this structure:

---

**Weekly Report — [Account Name] — Week of [Date]**

**At a glance**
- Reach: X (↑/↓ vs last week if available)
- Impressions: X
- New followers: +X
- Profile visits: X

**Best post this week**
[Caption excerpt] · [media_type] · [date]
→ X saves · X reach · X% engagement rate
[permalink]

**What's working**
[2–3 sentences from Llama or Claude analysis on patterns]

**Watch out for**
[1–2 sentences on lowest performer or trend to address]

**Recommended next step**
[One specific, actionable suggestion based on the data]

---

Offer to generate an HTML dashboard: "Want me to turn this into a visual report you can share with your team?"
