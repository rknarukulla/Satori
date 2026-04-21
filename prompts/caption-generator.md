# Prompt: Caption Generator

Use when the user asks you to write a caption for a new post.

---

## Instructions for Claude

### 1. Gather context
If the user hasn't specified, ask exactly one question:
> "What's the post about? (One sentence is fine — topic, format, and what you want the audience to do.)"

Don't ask multiple questions. Work with what you have.

### 2. Analyze brand voice from data (if not provided in config)
Fetch last 10 posts sorted by saves:
```
GET /{account_id}/media
  ?fields=id,caption,timestamp
  &limit=30
  &access_token={token}
```
Then fetch saves for each:
```
GET /{media_id}/insights?metric=saved&access_token={token}
```

From the top-save captions, extract:
- Average caption length (character count)
- Emoji usage: yes/no, density, style
- Hashtag count and placement (inline vs end)
- CTA style: question / command / open-ended
- Tone: casual / authoritative / vulnerable / educational
- Common opener patterns (question, statement, story, stat)

### 3. Check config for brand_voice and niche
If `brand_voice` is set, use it. If `niche` is set, use it to inform hashtag selection.

### 4. Generate 3 caption variants

**Variant A — Curiosity hook**
Opens with a question or surprising statement that creates a knowledge gap.

**Variant B — Social proof hook**
Opens with a result, user experience, or credibility signal.

**Variant C — Direct CTA hook**
Opens with the action or benefit immediately — no preamble.

Each caption should:
- Match the tone and length pattern of the account's top performers
- Include a natural CTA at the end
- Include 5–8 hashtags that match the niche (placed at end unless account style differs)
- Use emojis only if the account's top posts use them

### 5. Add a recommendation
After the 3 variants, add one line:
> **My pick:** Variant [X] — [one-sentence reason based on what's historically worked]

### 6. Offer to refine
"Want me to adjust the tone, shorten it, or swap the hashtags for a specific audience?"

---

## Output format

```
**Caption A — Curiosity**
[Caption text]

**Caption B — Social Proof**
[Caption text]

**Caption C — Direct CTA**
[Caption text]

**My pick:** Variant B — your last 3 carousels with social proof hooks averaged 2× the saves of question openers.
```
