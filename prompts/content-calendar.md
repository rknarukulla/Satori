# Prompt: Content Calendar Generator

Use when the user asks for a content plan, calendar, or "what should I post this month."

---

## Instructions for Claude

### 1. Determine the planning window
Default: the next 30 days (current date + 30).
If the user specifies a month or number of weeks, use that.

### 2. Analyze historical performance (last 60 days)
Fetch last 40 posts with insights:
```
GET /{account_id}/media
  ?fields=id,caption,media_type,timestamp
  &limit=40
  &access_token={token}
```
For each, fetch:
```
GET /{media_id}/insights?metric=reach,saved,engagement&access_token={token}
```

Compute:
- **Best media_type** by avg saves: IMAGE / REEL / CAROUSEL_ALBUM
- **Best posting days**: group by day of week, avg reach per day
- **Best posting times**: group by hour (from timestamp), avg engagement
- **Top caption patterns**: opener style, length, hashtag count
- **Top content themes**: cluster captions by topic (infer from keywords)

### 3. Check audience active hours
```
GET /{account_id}/insights
  ?metric=online_followers
  &period=lifetime
  &access_token={token}
```
Use peak hours to recommend posting windows.

### 4. Run trend research (WebSearch)
Search: "[niche from config] Instagram trends [current month] [current year]"
Pull 2–3 trending topics or formats relevant to the account's niche.

### 5. Build the calendar

Generate a 4-week plan. For each week, plan 3–5 posts (typical posting frequency — adjust if historical data shows a different rhythm).

Each entry includes:
- **Day & Date**
- **Format**: Reel / Carousel / Static Image
- **Topic / Angle**: specific idea, not generic
- **Caption hook**: the opening line or hook style
- **Hashtag cluster**: 5–8 hashtags grouped by theme
- **Goal**: reach / saves / comments / shares

Prioritize:
- Formats with the highest historical performance
- Days/times with highest audience activity
- At least one trend-aligned post per week
- Content variety: don't repeat the same format twice in a row

### 6. Output format

```
## Content Calendar — [Month] [Year] — @[account_name]

### Week 1 (Apr 1–7)

| Day | Format | Topic | Hook | Goal |
|-----|--------|-------|------|------|
| Tue Apr 1 | Carousel | [topic] | [hook] | Saves |
| Thu Apr 3 | Reel | [topic] | [hook] | Reach |
| Sat Apr 5 | Image | [topic] | [hook] | Comments |

Hashtag clusters:
- **Cluster A (niche)**: #tag1 #tag2 #tag3 #tag4 #tag5
- **Cluster B (broader)**: #tag1 #tag2 #tag3 #tag4 #tag5

...repeat for weeks 2–4...

### Strategy notes
- [2–3 sentences on the overall approach for this month]
- Best window to post: [day] [time range] based on your audience data
- Format to prioritize: [type] — [reason from data]
```

### 7. Offer to save
"Want me to save this as an HTML file you can share with your team?"

If yes, write to `reports/calendar-{YYYY-MM}.html` — a clean table layout with color-coded format types.
