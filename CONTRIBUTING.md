# Contributing to Satori

Thanks for being here. Satori is an open source project with a simple goal: give anyone conversational analytics over their own data, with no subscriptions and no servers.

There are three ways to contribute — pick whichever fits your skills.

---

## 1. Build a platform fork

The biggest contribution you can make is building Satori for a different platform. The architecture (`agents.md` + `skills/` + `config.yaml`) is designed to be forked — swapping the Instagram layer for LinkedIn, YouTube, Shopify, or any REST API takes a few hours, not weeks.

**Platforms waiting to be built:**

| Platform | API | Status |
|---|---|---|
| LinkedIn | LinkedIn Marketing API | Open |
| YouTube | YouTube Data API v3 | Open |
| TikTok | TikTok for Developers API | Open |
| Shopify | Shopify Admin API | Open |
| Google Analytics | GA4 Data API | Open |
| Twitter/X | Twitter API v2 | Open |

**To claim a platform:**
1. Open a [GitHub Discussion](../../discussions) in the **Platform Forks** category
2. Say which platform you're building — we'll mark it as claimed so nobody duplicates effort
3. Fork this repo, build it, open a PR when ready
4. We'll link your fork from this repo's README

Read `docs/pattern-guide.md` for the exact steps to fork for a new platform. It takes about 2–3 hours for someone comfortable with REST APIs.

---

## 2. Improve the Instagram skill

Found a gap, an outdated API endpoint, or a better way to handle a particular question? The skill files are plain markdown — no code required.

**Good places to contribute:**

- `skills/creator.md` / `skills/business.md` — better advice for specific niches (fitness creators, local restaurants, SaaS companies)
- `skills/stay-current.md` — better sources for algorithm updates, better search queries
- `prompts/` — new prompt templates for use cases we haven't covered
- `docs/token-setup.md` — clearer steps, better troubleshooting for edge cases

**To contribute a skill improvement:**
1. Fork the repo
2. Edit the relevant `.md` file
3. Open a PR with a one-sentence description of what changed and why
4. No tests required — just explain what problem it solves

---

## 3. Share feedback and ideas

Not ready to write code or markdown? Use [GitHub Discussions](../../discussions) to:

- **Show & Tell** — share a report Satori generated, a caption it wrote, a use case you found
- **Ideas** — suggest a feature, a new skill, a platform fork you'd use
- **Q&A** — ask how something works or how to set up a specific use case
- **Platform Forks** — claim a platform you're building

Good feedback shapes the roadmap. We read everything.

---

## What makes a good PR

- **One change per PR.** Don't bundle unrelated improvements.
- **Explain the why, not just the what.** "Updated Llama endpoint" is less useful than "Updated Llama endpoint — the old one was deprecated in March 2026."
- **Test your change.** If you edit a skill file, open the folder in your AI tool and verify the routing still works and the advice makes sense.
- **No breaking changes without discussion first.** If your change affects `agents.md` routing or `skills/onboarding.md`, open a Discussion before a PR so we can align.

---

## Project values

**Privacy over convenience.** Every design decision should keep user data local. If a feature requires sending data to a third-party server, it needs a very strong reason.

**Plain language over technical jargon.** The target user is a creator or small business owner, not a developer. Skill files and docs should be readable by someone who has never heard of an API.

**One source of truth.** `agents.md` is the router. Skills are loaded on demand. Don't duplicate logic across files — if something belongs in `skills/creator.md`, it shouldn't also be in the weekly summary prompt.

**Forks over features.** A new platform fork is more valuable than a new feature on Instagram. The pattern is the product.

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers this project.
