# Skill: Llama AI Integration

Loaded only when `llama.api_key` is present in config. Provides two capabilities: metric narrative analysis and visual post analysis.

Base URL: `https://api.llama.com/v1/`
Auth: `Authorization: Bearer {llama_api_key}` header.

---

## When to Use Llama

| Situation | Use |
|---|---|
| Weekly or monthly review | Llama 3.3-70B for metric narrative |
| Monthly top/bottom post review | Llama 3.2-Vision on images |
| Comment analysis (50+ comments) | Llama 3.3-70B for sentiment clustering |
| Pattern detection across many posts | Llama 3.3-70B |
| Single caption question | Skip Llama — Claude alone is sufficient |
| < 10 posts (cold start) | Skip Llama — not enough data for pattern analysis |

Don't call Llama for every question. Use it when the dataset is large enough to benefit from a second analytical pass.

---

## Model 1: Llama 3.3-70B — Metric Narrative

Use for: turning raw metric JSON into readable insight, spotting patterns across many posts, identifying anomalies.

```
POST https://api.llama.com/v1/chat/completions
Headers:
  Authorization: Bearer {llama_api_key}
  Content-Type: application/json

Body:
{
  "model": "Llama-3.3-70B-Instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are an Instagram analytics expert. Given raw metric data, identify the single most important pattern, anomaly, or opportunity in 3–5 sentences. Be specific. Name the post type, the metric, and the actionable implication. Do not hedge."
    },
    {
      "role": "user",
      "content": "{metric_json}"
    }
  ],
  "max_tokens": 300,
  "temperature": 0.3
}
```

**Account-type context:** append to the system prompt:
- Creator: "This is a personal creator account. Focus on engagement rate, saves, and follower growth as success signals."
- Business: "This is a business account. Focus on saves (purchase intent), profile visits, and reach to non-followers as success signals."

---

## Model 2: Llama 3.2-Vision — Post Visual Analysis

Use for: analyzing the top 5 and bottom 5 posts by saves during monthly reviews, or when the user asks to analyze a specific post's image.

```
POST https://api.llama.com/v1/chat/completions
Headers:
  Authorization: Bearer {llama_api_key}
  Content-Type: application/json

Body:
{
  "model": "Llama-3.2-11B-Vision-Instruct",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url": "{media_url}" }
        },
        {
          "type": "text",
          "text": "Analyze this Instagram post image. Cover: (1) composition and subject placement, (2) color palette and contrast, (3) text overlay legibility (if any), (4) visual hierarchy — what the eye goes to first, (5) one specific element that likely helps or hurts saves and shares. Be specific, not generic."
        }
      ]
    }
  ],
  "max_tokens": 250
}
```

Only use Vision when `media_url` is available. Skip gracefully for posts where the image URL has expired.

---

## Model 3: Llama 3.3-70B — Comment Sentiment

Use for: batch processing comment text to find themes, recurring questions, and sentiment signals.

```
POST https://api.llama.com/v1/chat/completions

Body:
{
  "model": "Llama-3.3-70B-Instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are analyzing Instagram comments. Identify: (1) overall sentiment — positive, neutral, or negative with a rough percentage breakdown, (2) the top 3 recurring themes or questions people are raising, (3) any negative sentiment spikes worth addressing. Be concise and specific."
    },
    {
      "role": "user",
      "content": "Comments:\n{comment_text_joined_by_newlines}"
    }
  ],
  "max_tokens": 200,
  "temperature": 0.2
}
```

Only run this when there are 20+ comments. Below that threshold, Claude can read and summarize comments directly without a Llama call.

---

## Synthesizing Llama + Claude Output

Llama provides the pattern. Claude provides the action.

After receiving Llama's response:
1. Quote the key insight from Llama (clearly attributed: "The data shows...")
2. Add Claude's recommendation on what to do with it ("Based on this, the next post should...")
3. Never just paste Llama's raw output — synthesize it into the conversation flow.

---

## Graceful Degradation (no Llama key)

If `llama.api_key` is empty or missing:
- Skip all Llama calls silently
- Claude's own analysis replaces Llama's — it's still high quality, just without the second pass
- Do not tell the user "Llama is unavailable" on every response — only mention it once if they ask why there's no visual analysis
- Optionally suggest: "Adding a Llama API key in config.yaml will enable visual post analysis and richer metric narratives."
