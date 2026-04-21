# Skill: Meta Graph API Reference

Loaded when any API call is needed. Contains all endpoints, field lists, and data extraction patterns.

**This file is a baseline reference — not a live source of truth.** Before a weekly review or when hitting unexpected errors, load `skills/stay-current.md` to check for deprecated endpoints, new API versions, or changed field names. If stay-current reports a newer API version, substitute it for `v18.0` in all calls below.

Base URL: `https://graph.facebook.com/v18.0/`
Auth: append `&access_token={token}` to every request.

---

## Account-Level Endpoints

### Account info
```
GET /{account_id}?fields=name,username,followers_count,media_count,biography,website
```
Returns: display name, handle, follower count, total post count, bio, website URL.

### Account insights (time-series)
```
GET /{account_id}/insights
  ?metric=reach,impressions,profile_views,follower_count
  &period=day
  &since={unix_timestamp}
  &until={unix_timestamp}
```
Returns: daily values for each metric over the window. Sum for totals; diff first/last for follower delta.

### Audience demographics
```
GET /{account_id}/insights
  ?metric=audience_city,audience_country,audience_gender_age
  &period=lifetime
```
Returns: top cities, countries, gender/age breakdown. Use for "who is your audience" questions.

### Online followers by hour
```
GET /{account_id}/insights
  ?metric=online_followers
  &period=lifetime
```
Returns: nested object of day → hour → follower count online. Use to recommend best posting times.

---

## Media Endpoints

### Fetch posts (with fields)
```
GET /{account_id}/media
  ?fields=id,caption,media_type,timestamp,like_count,comments_count,media_url,thumbnail_url,permalink
  &limit={n}
```
- `media_type` values: `IMAGE`, `VIDEO`, `REEL`, `CAROUSEL_ALBUM`
- `thumbnail_url` is set for videos/reels; `media_url` for images
- Default limit: 20. Max: 100 per call. Paginate via `after` cursor for more.
- Filter to a date range client-side by checking `timestamp`.

### Per-post insights
```
GET /{media_id}/insights
  ?metric=reach,impressions,saved,shares,engagement,plays
```
- `plays` only available for REELs — skip for IMAGE/CAROUSEL
- `saved` = number of saves (strongest value signal)
- `engagement` = likes + comments + saves + shares combined

### Comments on a post
```
GET /{media_id}/comments
  ?fields=text,timestamp,username
  &limit=100
```
Requires `instagram_manage_comments` permission. If absent, skip gracefully — note the permission needed.

---

## Story Endpoints

### Active stories (only available within 24h of posting)
```
GET /{account_id}/stories
  ?fields=id,timestamp,media_type,media_url
```

### Story insights
```
GET /{story_id}/insights
  ?metric=exits,impressions,reach,replies,taps_forward,taps_back
```
- `exits` = viewers who left mid-story
- `taps_forward` = skipped to next story (losing them)
- `taps_back` = rewatched (strong engagement signal)
- Completion rate = 1 - (exits / impressions)

**Critical:** story data disappears from the API 24 hours after posting. Always save to `data/stories-{date}.json` immediately.

---

## Hashtag Endpoints

### Find hashtag ID
```
GET /ig_hashtag_search
  ?user_id={account_id}
  &q={hashtag_without_#}
```
Returns a hashtag ID needed for the next call.

### Top posts for a hashtag
```
GET /{hashtag_id}/top_media
  ?user_id={account_id}
  &fields=id,media_type,timestamp,like_count,comments_count
```
Use for competitor/niche research. Shows publicly visible top posts for the hashtag.

---

## Pagination

Long media lists use cursor-based pagination. The response includes:
```json
{
  "data": [...],
  "paging": {
    "cursors": { "after": "CURSOR_STRING" },
    "next": "https://graph.facebook.com/..."
  }
}
```
Fetch `paging.next` to get the next page. Stop when no `next` key is present.

---

## Derived Metric Calculations

Always compute these from raw API data — the API does not return them directly:

```
Engagement rate    = (likes + comments + saves + shares) / reach × 100
Save rate          = saves / reach × 100
Share rate         = shares / reach × 100
Follower delta     = follower_count[last_day] - follower_count[first_day]
Story completion   = 1 - (exits / impressions)
Reach/follower ratio = post_reach / followers_count × 100
```

---

## Unix Timestamp Conversion

Meta's API uses Unix timestamps for `since`/`until` parameters. Compute:
- Today: current date at 00:00:00 UTC → Unix timestamp
- 7 days ago: today minus 604800 seconds
- 30 days ago: today minus 2592000 seconds

---

## Data Snapshot Pattern

After any significant data fetch, write to `data/`:
```
data/snapshot-{YYYY-MM-DD}.json   ← full account + media + insights
data/stories-{YYYY-MM-DD}.json    ← stories only (expire in 24h)
```

When answering trend questions, read existing snapshots first before re-fetching. Saves API calls and enables historical comparison across sessions.
