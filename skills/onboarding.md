# Skill: Onboarding

Handles three scenarios: first-time setup, missing account_type, and cold start (new account with < 10 posts).

---

## Scenario A — First Run (no config.yaml)

1. Greet the user:
   > "Welcome to Satori. I'll help you understand and grow your Instagram — no dashboards, just conversation. First, let's connect your account. It takes about 3 minutes."

2. Ask two quick questions before token setup:
   - "Are you a **content creator** (personal brand, influencer, educator) or a **business** (brand, product, service, local business)?"
   - "What's your niche or what does your account focus on? (One sentence is fine.)"

3. Direct them to `docs/token-setup.md`. Explicitly tell them:
   > "Follow the steps in that doc. At the end, it will ask you to save your token directly into `config.yaml` — do that instead of pasting it here. Tokens are sensitive, like passwords. Once you've saved the file, come back and just tell me you're done."

4. Once they say they're done, **read `config.yaml` silently using the Read tool** — do not ask them to paste anything. The token comes from the file, never from chat.

5. With the token from config, look up their Account ID automatically:
   ```
   GET /me/accounts?access_token={token}
   ```
   Find the Facebook Page linked to their Instagram, then:
   ```
   GET /{page_id}?fields=instagram_business_account&access_token={token}
   ```
   Extract the `instagram_business_account.id`. The user never sees this step.

6. Update `config.yaml` with the discovered `account_id` and `account_name` using the Edit tool. Write `config.yaml` with everything filled in:
   ```yaml
   meta:
     token: "{their_token}"
     account_id: "{their_account_id}"
     account_name: "{their_handle}"
   account_type: "{creator or business}"
   niche: "{what they said}"
   goals: ""
   llama:
     api_key: ""
   satori:
     timezone: "America/New_York"
     brand_voice: ""
   ```

5. Verify setup — call:
   ```
   GET /{account_id}?fields=name,username,followers_count,media_count&access_token={token}
   ```
   Greet them: "You're connected, @{username}. {followers_count} followers, {media_count} posts. Let's get to work."

6. If `media_count < 10` → continue to **Scenario C** immediately.
7. Otherwise → read `skills/creator.md` or `skills/business.md` based on account_type and proceed.

---

## Scenario B — account_type Missing from config.yaml

Config exists but `account_type` is blank or missing.

1. Ask once:
   > "Quick question before we start — are you using this account as a **content creator** (personal brand, influencer) or as a **business** (brand, product, service)? This shapes the advice I give you."

2. Write the answer into `config.yaml` under `account_type`.
3. Load the appropriate skill file and continue.

---

## Scenario C — Cold Start (media_count < 10)

The account is new or has very few posts. Data-driven analysis isn't possible yet. Switch to launch mode.

### What to tell the user
> "Your account is just getting started — {media_count} posts so far. I can't spot your patterns yet, but I can help you build the right foundation from day one. Here's what we can do right now:"

### What Satori CAN do in cold start

**Content strategy from scratch**
- WebSearch trending content formats in their niche right now
- Identify 3 content pillars based on niche + account type
- Build a first 30-day content calendar using best practices (not account history)
- Recommend posting frequency based on account type (see below)

**Caption writing**
- Write captions using niche best practices and account type tone (no account history needed)
- Load `prompts/caption-generator.md` — it handles the no-history case

**Competitor research**
- Ask: "Who are 2–3 accounts in your niche you admire?"
- WebFetch their public profile data for benchmarks (public posts only, within ToS)
- Use as proxy for "what works in this niche" until their own data exists

**Setup for data accumulation**
- Explain which metrics matter most for their account type
- Tell them to schedule a weekly Satori session so data builds up
- Note: story data expires in 24h — mention they should check in daily or schedule it

### Feature unlock milestones — tell the user upfront

| Posts | What unlocks |
|---|---|
| 10 | Basic pattern detection (best media type, caption length) |
| 20 | Reliable engagement benchmarks, brand voice inference |
| 30 | Content calendar built from their own data |
| 60 | Trend analysis, anomaly detection, audience timing data |

### Posting frequency recommendations (cold start)

**Creator:** 4–5x per week — algorithm rewards consistency early on. Mix reels (reach) and carousels (saves).

**Business:** 3–4x per week — quality over volume. Prioritize carousels (saves = purchase intent signal) and one reel per week for reach.

### What NOT to do in cold start
- Don't fabricate engagement benchmarks from their nonexistent data
- Don't run weekly summary (nothing meaningful to summarize)
- Don't tell them what "works for their account" — use niche best practices instead, and say so explicitly
