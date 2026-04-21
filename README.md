# Satori

**Your Instagram data stays between you and Meta. No subscription. No dashboard. Just ask.**

Every analytics tool on the market stores your Instagram data on their servers, charges you monthly, and makes you navigate a dashboard to find answers. Satori does none of that. Open this folder in any AI coding tool, ask a question in plain English, and get an answer — powered by your own Meta token, running entirely on your machine.

Free. Open source. Private by architecture, not by policy.

---

## What you can ask

```
"How did my posts perform last week?"
"What should I post this week?"
"Write a caption for our new product launch."
"Plan my content for May."
"Analyze this post: https://www.instagram.com/p/..."
"How are my stories doing?"
"Give me a dashboard I can share with my team."
```

No forms to fill. No reports to schedule. No charts to navigate. Ask, get an answer, act.

---

## What it does

- **Weekly performance summaries** — reach, engagement, follower growth, top posts
- **Post deep-dives** — per-post metrics, visual analysis (via Llama Vision), comment sentiment
- **Caption generation** — 3 variants in your account's brand voice, based on what's historically worked
- **Content calendars** — 30-day plans built from your data and current trends
- **Anomaly detection** — engagement drops, sentiment spikes, story completion changes
- **HTML dashboards** — self-contained reports you can open in any browser or share with your team

All data comes from Meta's official Graph API with your own token. Your Instagram credentials and account data are read locally and sent only to Meta's official API — never to a third-party analytics server, never stored in someone else's database. The AI conversation layer runs through your chosen AI tool (Claude, Cursor, etc.) under that tool's own privacy policy.

---

## Setup — 3 steps

### 1. Open this folder in Claude Code

Download or clone this repo. Open the folder in Claude Code (the desktop app or VS Code extension).

Your AI tool will read `agents.md` automatically and introduce itself as Satori.

### 2. Get a Meta access token

Claude will walk you through this, or follow `docs/token-setup.md` directly.

It takes ~3 minutes. You need:
- An Instagram Business or Creator account
- A Facebook Developer account (free — same login)

### 3. Add your token to config.yaml

```bash
cp config.yaml.example config.yaml
```

Open `config.yaml` and fill in your token and account ID. Claude will find your account ID for you if needed.

Tell Claude "I'm set up" — it will verify by fetching your account name and you're done.

---

## Usage examples

```
"How did my posts perform last week?"
"What should I post this week?"
"Write a caption for our new feature launch."
"Plan my content for May."
"Analyze this post: https://www.instagram.com/p/..."
"How are my stories doing?"
"Give me a dashboard I can share with my team."
```

---

## How it works

```
You ask Claude a question
    │
    ├── Claude reads config.yaml for your token
    ├── WebFetch → graph.facebook.com (Meta Graph API)
    ├── WebFetch → api.llama.com (Llama analysis, optional)
    ├── Claude reasons over the data
    └── Claude answers in plain English (+ optional HTML report)
```

No Python. No local servers. No pip install. Claude is the orchestrator, the analyst, and the interface.

---

## File structure

```
satori/
├── CLAUDE.md              ← auto-loaded by Claude Code
├── agents.md              ← agent role definition and routing (tool-agnostic)
├── config.yaml.example    ← credentials template
├── config.yaml            ← your credentials (gitignored)
│
├── prompts/
│   ├── weekly-summary.md
│   ├── post-analysis.md
│   ├── caption-generator.md
│   └── content-calendar.md
│
├── data/                  ← raw API snapshots (gitignored)
├── reports/               ← generated HTML reports
│
└── docs/
    ├── token-setup.md     ← step-by-step token guide
    ├── api-permissions.md ← what each permission does
    └── pattern-guide.md   ← how to fork for other platforms
```

---

## Optional: Llama AI layer

For richer analysis, add a Llama API key to `config.yaml`. This enables:

- **Llama 3.3-70B** — narrative analysis of your metrics, pattern detection across historical data
- **Llama 3.2-Vision** — visual analysis of your post images (what composition, color, and subject placement correlates with saves)
- **Comment sentiment clustering** — what people keep asking, what's getting negative reactions

Get a key at [llama.developer.meta.com](https://llama.developer.meta.com/). The Llama API is free for most usage levels.

Without a Llama key, Satori still works well — Claude's own analysis is substantial.

---

## Scheduled reports

Use Claude Code's Schedule skill to automate weekly reports:

```
/schedule every Monday at 9am: run the weekly summary for my Instagram account
```

This will auto-fetch your data and write a fresh HTML report to `reports/` every Monday before you open your laptop.

Story data expires from the API in 24 hours — schedule a daily story fetch to accumulate it before it's gone.

---

## Fork for other platforms

Satori is the first working example of a reusable pattern:

**agents.md + config.yaml + any capable AI tool = conversational intelligence for any REST API**

See `docs/pattern-guide.md` for how to fork this for LinkedIn, YouTube, Shopify, Stripe, or any platform with a REST API.

Community forks built on this pattern: *(coming soon)*

---

## Open source

MIT License. Built by [@ravinarukulla](https://github.com/ravinarukulla) — used internally first, then shared.

**Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md) — you can improve the Instagram skill, build a fork for another platform, or just share feedback and ideas in [GitHub Discussions](../../discussions).

Community forks built on this pattern: *(be the first — claim a platform in Discussions)*

---

## Meta compliance

Satori uses the official Meta Graph API with user-provided tokens. All data accessed belongs to the account owner. No scraping, no unofficial endpoints, no third-party data storage. Read-only access only.

See `docs/api-permissions.md` for exactly what each permission does.
