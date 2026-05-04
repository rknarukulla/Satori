# Manual Fetch — Cowork Setup

Use this when running Satori in Claude Cowork (claude.ai/code) or any environment where direct HTTP calls to `graph.facebook.com` are blocked.

---

## How it works

A small local script (`fetch.py`) runs on your machine — outside the sandbox — calls the Meta Graph API, and saves your data to `data/snapshot-{today}.json`. Satori reads from that file. No curl commands, no copy-pasting.

```
Your Terminal          Your Machine           Cowork Sandbox
─────────────         ──────────────         ──────────────
python fetch.py  →   data/snapshot.json  ←   Satori reads it
    ↕
Meta Graph API
```

---

## First-time setup

You only need to do this once:

```bash
python fetch.py
```

That's it. The script will:
- Auto-install `pyyaml` if needed (one-time, takes ~5 seconds)
- Read your credentials from `config.yaml`
- Fetch your account info, last 50 posts, and all post insights
- Save everything to `data/snapshot-{today}.json`
- Print a summary when done

---

## Refreshing your data

Run `python fetch.py` again anytime you want up-to-date metrics. Weekly is usually enough unless you're tracking a specific post's performance in real-time.

Satori will tell you at the start of each session how old your snapshot is.

---

## Config

`config.yaml` already has `satori.mode: manual-fetch` set. No changes needed — Satori handles the rest automatically.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `config.yaml not found` | Run `python fetch.py` from inside the Satori folder |
| `Token expired or invalid` | Refresh token at developers.facebook.com/tools/explorer/, update `meta.token` in config.yaml |
| `No module named yaml` | Run `pip install pyyaml` then retry |
| Python not found | Install Python 3 from python.org (free, 2-minute install) |
| Snapshot is stale | Just run `python fetch.py` again |
