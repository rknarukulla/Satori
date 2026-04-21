# Prompt: Single Post Deep-Dive

Use when the user shares a post URL, permalink, or media ID and wants detailed analysis.

---

## Instructions for Claude

### 1. Extract the media ID
- If the user provides a permalink (e.g., `https://www.instagram.com/p/ABC123/`), extract the short code and resolve it.
- If the user provides a media ID directly, use it.
- If neither, ask: "Can you share the post link or the post ID?"

### 2. Fetch post data
```
GET /{media_id}
  ?fields=id,caption,media_type,timestamp,like_count,comments_count,media_url,thumbnail_url,permalink
  &access_token={token}
```

### 3. Fetch post insights
```
GET /{media_id}/insights
  ?metric=reach,impressions,saved,shares,engagement,plays
  &access_token={token}
```
Note: `plays` is only available for REELs.

### 4. Fetch top comments (up to 50)
```
GET /{media_id}/comments
  ?fields=text,timestamp,username
  &limit=50
  &access_token={token}
```

### 5. Visual analysis (if llama_api_key is set and media_url is available)
Send the image to Llama 3.2-Vision with:
> "Analyze this Instagram post image. Comment on: composition, color palette, subject placement, text overlay (if any), visual hierarchy, and what elements likely drive or hurt saves and shares. Be specific."

### 6. Benchmark against account average
Read `data/` snapshots or fetch the last 20 posts to compute account averages:
- Avg reach, avg saves, avg engagement rate
- This post's percentile ranking: "This post is in the top X% for saves"

### 7. Comment sentiment (if llama_api_key is set)
Send comment text to Llama 3.3-70B:
> "These are comments on an Instagram post. Identify: overall sentiment (positive/neutral/negative), the top 3 recurring themes or questions, and any negative sentiment worth addressing."

### 8. Generate response

---

**Post Analysis — [Caption excerpt] — [Date]**

**Performance**
| Metric | This Post | Account Avg |
|---|---|---|
| Reach | X | X |
| Saves | X | X |
| Shares | X | X |
| Engagement rate | X% | X% |
| Plays (reels) | X | X |

**Percentile ranking**: This post is in the top X% for saves on your account.

**Visual analysis** *(Llama Vision)*
[3–5 sentences on composition, color, visual hooks]

**What the comments say**
[2–3 sentences on sentiment and themes]

**What made this work / What held it back**
[Honest assessment: what specific elements drove or limited performance]

**Replicate or avoid?**
[Direct recommendation on whether to repeat this format/angle]
