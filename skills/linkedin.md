# Satori — LinkedIn Skill

Load this file when the user asks about: LinkedIn metrics, Company Page performance, LinkedIn post engagement, follower growth, impressions, reach, or anything LinkedIn-specific.

---

## Config Fields (read from config.yaml)

```
linkedin.access_token  ← OAuth2 Bearer token (expires every 60 days)
linkedin.org_id        ← Company Page numeric ID (not the vanity URL slug)
linkedin.org_name      ← Display name for reports
```

---

## Data Mode Detection

**Check for a snapshot first:**
Look for the most recent file matching `data/snapshot-linkedin-*.json`. Read it.
- If found and ≤ 7 days old: use it as the data source. Proceed normally.
- If found but > 7 days old: use it, but note: *"Your LinkedIn snapshot is from {date}. Run `python fetch_linkedin.py` in Terminal to refresh it."*
- If not found: tell the user: *"I need you to run `python fetch_linkedin.py` once in Terminal to pull your LinkedIn data. Once done, come back and I'll have everything I need."*

**Direct HTTP mode** (when no snapshot exists and WebFetch is available):
Read `linkedin.access_token` from config.yaml and use it as a Bearer token directly. No signing required — LinkedIn uses plain OAuth2 tokens.

---

## Auth (direct mode)

LinkedIn API uses a standard Bearer token — no JWT construction needed.

Read `linkedin.access_token` from config.yaml. Use for all requests:
```
Authorization: Bearer {access_token}
LinkedIn-Version: 202312
X-Restli-Protocol-Version: 2.0.0
```

**Token expiry:** LinkedIn access tokens expire after 60 days. If a request returns 401, tell the user to refresh their token (see `docs/linkedin-setup.md`) and update `linkedin.access_token` in config.yaml.

---

## API Endpoints

Base URL: `https://api.linkedin.com/v2`

| Data | Endpoint |
|---|---|
| Org info + follower count | `GET /organizations/{orgId}?projection=(id,name,localizedName,followerCount,vanityName)` |
| Follower statistics (demographics) | `GET /organizationalEntityFollowerStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{orgId}` |
| Share/engagement stats (30d, daily) | `GET /organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{orgId}&timeIntervals.timeGranularityType=DAY&timeIntervals.timeRange.start={ms}&timeIntervals.timeRange.end={ms}` |
| Recent posts | `GET /ugcPosts?q=authors&authors=List(urn:li:organization:{orgId})&count=20&sortBy=LAST_MODIFIED` |
| Per-post stats (batch, up to 20) | `GET /organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={URN}&shares=List({postUrn1},{postUrn2},...)` |

**Timestamps:** LinkedIn uses millisecond epoch timestamps. `now_ms = unix_timestamp * 1000`.

**Org URN format:** Always use `urn:li:organization:{orgId}` — this is required by the API, not the plain numeric ID.

---

## Derived Metrics

| Metric | How to compute |
|---|---|
| Total followers | `org_info.followerCount` |
| Organic followers | From `followerStats` — `followerCountsByAssociationType` where `associationType = MEMBER` |
| Engagement rate | `(reactions + comments + shares) / impressions × 100` per post |
| CTR | `clicks / impressions × 100` |
| Avg impressions per post | Total impressions (30d) / number of posts published in period |
| Top post | Highest `impressionCount` in `post_stats` |
| Follower seniority mix | From `followerCountsByFunction` in follower stats |

---

## Analysis Framing

Lead with the most actionable signal — in this order:
1. **Follower count + growth** — total followers and trend; flag if follower growth stalled
2. **Impressions trend** — 30-day total and weekly trajectory; LinkedIn reach is algorithm-driven and can shift sharply
3. **Engagement rate** — LinkedIn benchmark is ~1–3% for company pages; anything above 3% is strong
4. **Top performing posts** — surface the top 2–3 posts by impressions and explain what they have in common
5. **CTR** — low CTR with high impressions = content gets seen but doesn't compel action; review CTAs
6. **Audience demographics** — seniority, industry, function mix (if follower_stats available); useful for content targeting

LinkedIn-specific context to include where relevant:
- LinkedIn's algorithm heavily favors dwell time and early engagement — posts that get comments in the first hour are promoted significantly more
- Document posts and carousels consistently outperform text-only posts on LinkedIn; video is also strong
- Best posting cadence for company pages: 3–5x per week. Posting daily tends to cannibalize reach per post
- LinkedIn followers are more valuable than raw count suggests — even 1,000 highly relevant followers (CTOs, VPs) can drive significant pipeline
- Follower count doesn't reset or vary with content — it's a stable long-term metric; focus analysis on impressions and engagement instead

---

## Error Handling

| Error | Response |
|---|---|
| 401 Unauthorized | "Your LinkedIn access token has expired (they last 60 days). Refresh it in the LinkedIn Developer Portal and update `linkedin.access_token` in config.yaml. See `docs/linkedin-setup.md`." |
| 403 Forbidden | "Permission denied. Your LinkedIn app may be missing required OAuth scopes (`r_organization_social`, `rw_organization_admin`). See `docs/linkedin-setup.md` Step 2." |
| org_id not found | "Organization not found. Verify that `linkedin.org_id` in config.yaml is the numeric Company Page ID (not the vanity URL slug). See `docs/linkedin-setup.md` to find it." |
| No snapshot + direct blocked | "Direct API calls aren't available here. Run `python fetch_linkedin.py` in Terminal once and I'll read from the saved snapshot." |
| token missing | "No LinkedIn access token in config.yaml. See `docs/linkedin-setup.md` to generate one." |

---

## Snapshot Structure Reference

```json
{
  "fetched_at": "ISO timestamp",
  "platform": "linkedin",
  "org": {
    "id": "12345678",
    "name": "Your Company",
    "info": { "followerCount": 4200, "localizedName": "Your Company", "vanityName": "yourcompany" }
  },
  "follower_stats": [
    {
      "followerCountsByAssociationType": [
        { "associationType": "MEMBER", "followerCounts": { "organicFollowerCount": 4100, "paidFollowerCount": 100 } }
      ],
      "followerCountsByFunction": [ ... ],
      "followerCountsBySeniority": [ ... ]
    }
  ],
  "share_stats_30d": {
    "daily": [ { "timeRange": {}, "totalShareStatistics": { "impressionCount": 1200, "clickCount": 45, "likeCount": 38, "commentCount": 12, "shareCount": 7 } } ],
    "totals": { "impressions": 28000, "clicks": 940, "reactions": 720, "comments": 210, "shares": 95 }
  },
  "posts": [
    {
      "id": "urn:li:ugcPost:...",
      "specificContent": { "com.linkedin.ugc.ShareContent": { "shareCommentary": { "text": "Post text..." } } },
      "created": { "time": 1716000000000 },
      "stats": { "impressionCount": 3200, "clickCount": 140, "likeCount": 95, "commentCount": 18, "shareCount": 12 }
    }
  ]
}
```
