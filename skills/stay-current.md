# Skill: Stay Current

Loaded when the user asks about algorithms, latest features, recent changes, or when an API call returns an unexpected error that may indicate a platform change. Also loaded at the start of weekly/monthly reviews to ensure advice reflects current Instagram behaviour.

---

## When to Load This Skill

- User asks: "what's new", "has the algorithm changed", "why is my reach dropping", "are these tips still relevant", "what's working on Instagram right now"
- An API endpoint returns a deprecation warning or unexpected error
- Starting a weekly or monthly review (load once, skip if already loaded this session)
- User mentions a feature or metric that isn't in `skills/api-reference.md`

---

## Step 1 — Check Meta's Official Changelog

WebFetch the Meta Graph API changelog to check for API version changes, deprecated endpoints, and new fields:

```
WebFetch: https://developers.facebook.com/docs/graph-api/changelog
```

Look for:
- New API version (currently tracking v18.0 — flag if a newer version is available)
- Deprecated endpoints or fields that Satori uses
- New metrics or fields that could improve Satori's analysis
- Breaking changes to auth or permission scopes

```
WebFetch: https://developers.facebook.com/docs/instagram-api/changelog
```

Look for:
- Changes to Instagram-specific endpoints (media, insights, stories)
- New insight metrics available
- Changes to rate limits or token behaviour

---

## Step 2 — Check for Instagram Algorithm Updates

WebSearch for recent algorithm and platform behaviour changes:

```
WebSearch: "Instagram algorithm update {current_year}"
WebSearch: "Instagram reach algorithm changes {current_month} {current_year}"
WebSearch: "Instagram Reels algorithm {current_year}"
```

Pull from authoritative sources only — prefer:
- Instagram's official @creators account announcements
- Meta Newsroom (newsroom.fb.com)
- Social Media Examiner, Later, Hootsuite research blogs (secondary)

Ignore: clickbait articles, SEO farms, posts with no cited source.

---

## Step 3 — Check What's Currently Working

WebSearch for current content performance patterns:

```
WebSearch: "what content is performing best on Instagram {current_month} {current_year}"
WebSearch: "Instagram Reels vs carousel performance {current_year}"
WebSearch: "best time to post Instagram {current_year}"
```

Cross-reference findings with the user's own account data when available. Account data always beats general trends — general trends are the fallback when account history is thin.

---

## Step 4 — Synthesise and Apply

After fetching, produce a short internal summary (not shown to user unless they ask):

```
API version: v{X} — Satori currently uses v18.0 — [up to date / update needed]
Deprecated: [list any endpoints Satori uses that are deprecated]
New metrics: [any new fields worth using]
Algorithm signal: [1-2 sentence summary of current reach/engagement drivers]
Content format: [what format is currently favoured by the algorithm]
```

Apply findings immediately to the current session:
- If a better API version exists, use it in subsequent WebFetch calls
- If a deprecated endpoint is needed, use the replacement and note it
- If algorithm guidance differs from what's in `skills/creator.md` or `skills/business.md`, follow the fresher signal and flag the discrepancy to the user briefly

---

## Step 5 — Update the Session Snapshot

Write a lightweight update log to `data/platform-updates-{YYYY-MM-DD}.json`:

```json
{
  "checked_at": "{ISO timestamp}",
  "api_version_latest": "v{X}",
  "api_version_satori": "v18.0",
  "deprecated_endpoints": [],
  "new_metrics": [],
  "algorithm_summary": "...",
  "sources": ["url1", "url2"]
}
```

On future sessions, check if this file exists and was written within the last 7 days. If yes, read it instead of re-fetching — saves time and API calls. If older than 7 days, re-fetch.

---

## What to Tell the User

Keep it brief. After running this skill, mention only what actually changed or matters:

**If everything is current:**
> "I've checked Meta's latest docs and recent algorithm signals — nothing material has changed since last week. Carrying on with current guidance."

**If something changed:**
> "Quick note: Instagram recently [specific change]. I've adjusted my recommendations for this session accordingly. [One sentence on what that means for them specifically.]"

**If a deprecated endpoint is found:**
> "Meta has deprecated the [{endpoint}] call I was about to use. Switching to the updated version — no action needed from you."

Don't over-report. The user doesn't need a full changelog summary unless they ask for it.

---

## Scheduled Freshness Check

Recommend the user set up a weekly check using Claude Code's Schedule skill:

```
/schedule every Monday at 8am: check for Meta API and Instagram algorithm updates and summarise anything that affects my content strategy
```

This runs before the weekly summary, so the Monday report always reflects current platform behaviour.
