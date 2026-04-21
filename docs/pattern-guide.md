# The Claude API Intelligence Pattern

Satori is an Instagram tool, but it's also an example of a reusable architecture. This document explains the pattern so you can fork it for any REST API.

---

## The core insight

Claude can call any REST API via WebFetch. It can read the JSON response, reason over it, chain multiple calls, write files, and generate HTML — all within a Cowork session. This means:

> Any REST API + agents.md + a capable AI tool = a conversational intelligence product with zero local setup.

No Python. No scripts. No servers. No install step. The user opens a folder, the AI reads agents.md, and the product is running.

---

## Repository structure

```
your-tool/
│
├── CLAUDE.md              ← Claude Code adapter — tells Claude to read agents.md
├── .cursorrules           ← Cursor adapter
├── .github/copilot-instructions.md  ← Copilot adapter
├── agents.md               ← Claude's complete role definition (the brain)
├── config.yaml.example    ← credentials template (gitignored when filled)
├── .gitignore             ← protects config.yaml and data/
│
├── prompts/               ← reusable question templates
│   └── *.md
│
├── data/                  ← accumulated JSON snapshots (gitignored)
│   └── .gitkeep
│
├── reports/               ← generated HTML reports
│   └── .gitkeep
│
└── docs/
    ├── token-setup.md     ← how to get API credentials (the hard part)
    ├── api-permissions.md ← what each permission does
    └── pattern-guide.md   ← this file
```

---

## How to fork this for a different platform

### Step 1 — Rewrite agents.md

This is the only file you need to fundamentally change. Replace:
- The identity section (who Claude is in this context)
- The credentials section (what keys/tokens to read from config.yaml)
- The API endpoint reference (base URL, headers, endpoints)
- The "how to answer common questions" section (the domain-specific logic)
- The report generation section (what charts/tables make sense)

Keep the structure — it works. Just swap the domain.

### Step 2 — Update config.yaml.example

Replace `meta.token` and `meta.account_id` with whatever credentials the new API requires. Common patterns:

```yaml
# API key auth
api:
  key: "sk-..."

# OAuth token
oauth:
  token: "Bearer ..."
  
# Multiple services
stripe:
  secret_key: "sk_live_..."
hubspot:
  api_key: "..."
```

### Step 3 — Rewrite prompts/

Replace the Instagram-specific prompt templates with templates for your new domain. The structure stays the same:
- What data to fetch (which endpoints, in which order)
- How to compute derived metrics
- What format to output the response in

### Step 4 — Update docs/token-setup.md

The hardest part for users is always credential setup. Write clear, step-by-step instructions with direct links. Test it with a non-technical person before shipping.

### That's it.

Same CLAUDE.md. Same folder structure. Same Cowork flow. New data source.

---

## Platform examples

### LinkedInPulse (LinkedIn Marketing API)

```yaml
# config.yaml
linkedin:
  access_token: "AQV..."
  organization_id: "1234567"
```

Key agents.md changes:
- Base URL: `https://api.linkedin.com/v2/`
- Auth header: `Authorization: Bearer {token}` (not query param)
- Endpoints: `/organizationalEntityShareStatistics`, `/shares`, `/ugcPosts`
- Metrics: impressions, clicks, CTR, engagement rate, follower growth

### YTPulse (YouTube Data API)

```yaml
# config.yaml
youtube:
  api_key: "AIza..."
  channel_id: "UC..."
```

Key agents.md changes:
- Base URL: `https://www.googleapis.com/youtube/v3/`
- Auth: `key={api_key}` query param
- Endpoints: `/channels`, `/videos`, `/search`, `/videoCategories`
- Metrics: views, watch time, subscriber delta, CTR, avg view duration

### ShopifyPulse (Shopify Admin API)

```yaml
# config.yaml
shopify:
  shop: "mystore.myshopify.com"
  access_token: "shpat_..."
```

Key agents.md changes:
- Base URL: `https://{shop}/admin/api/2024-01/`
- Auth: `X-Shopify-Access-Token: {token}` header
- Endpoints: `/orders.json`, `/products.json`, `/customers.json`
- Metrics: revenue, AOV, conversion rate, top products, refund rate

---

## The Llama layer is also portable

The Llama API calls in agents.md are generic — they work for any metric narrative or vision task. The only things to change are the system prompt (domain-specific expertise) and the data you pass. The infrastructure is identical.

---

## What makes agents.md work well

After building Satori, here's what we learned about writing effective skill files:

**Be explicit about the data flow.** Tell Claude exactly which endpoints to call, in what order, and what to extract from each response. Don't assume it will figure it out.

**Include the error table.** API errors are the most common failure point. Anticipate them and tell Claude exactly what to say when they happen.

**Define the output format precisely.** "Respond in plain English" is underspecified. Use example output structures in the prompt templates so Claude's responses are consistent.

**Separate orchestration from templates.** agents.md handles the how-to and domain knowledge. The prompts/ files handle specific question patterns. This separation keeps agents.md readable.

**Test with a real token before publishing.** The hardest part of every API tool is the credential setup. Run through token-setup.md yourself and update it every time you find a confusing step.
