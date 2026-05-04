#!/usr/bin/env python3
"""
Satori fetch helper
Run this once in Terminal before opening Satori in Cowork:

    python fetch.py

Fetches your Instagram data from the Meta Graph API and saves it to
data/snapshot-{today}.json. Satori reads from that file automatically.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────

def load_config():
    try:
        import yaml
    except ImportError:
        print("Installing pyyaml (one-time setup)...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
        import yaml

    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌  config.yaml not found.")
        print("    Open Satori in Claude Code (terminal) first to complete setup.")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


# ── API helpers ───────────────────────────────────────────────────────────────

BASE = "https://graph.facebook.com/v18.0"


def api_get(path, params, token):
    params["access_token"] = token
    url = f"{BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())

    if "error" in data:
        err = data["error"]
        code = err.get("code", "?")
        msg = err.get("message", "Unknown error")
        if code == 190:
            print(f"\n❌  Token expired or invalid.")
            print("    Refresh your token at https://developers.facebook.com/tools/explorer/")
            print("    Then update meta.token in config.yaml and run fetch.py again.")
            sys.exit(1)
        raise RuntimeError(f"Meta API error {code}: {msg}")

    return data


def paginate(path, params, token, max_items=50):
    items = []
    data = api_get(path, params, token)
    items.extend(data.get("data", []))
    while len(items) < max_items:
        nxt = data.get("paging", {}).get("next")
        if not nxt:
            break
        with urllib.request.urlopen(nxt, timeout=15) as resp:
            data = json.loads(resp.read())
        items.extend(data.get("data", []))
    return items[:max_items]


# ── Fetch routines ─────────────────────────────────────────────────────────────

def fetch_account(account_id, token):
    print("  Fetching account info...", end=" ", flush=True)
    result = api_get(account_id, {
        "fields": "name,username,followers_count,media_count,biography,website"
    }, token)
    print("done")
    return result


def fetch_account_insights(account_id, token):
    print("  Fetching account insights (last 30 days)...", end=" ", flush=True)
    now = int(datetime.now(timezone.utc).timestamp())
    since = now - 30 * 24 * 3600
    try:
        result = api_get(f"{account_id}/insights", {
            "metric": "reach,follower_count",
            "period": "day",
            "since": since,
            "until": now,
        }, token)
        print("done")
        return result
    except RuntimeError as e:
        print(f"skipped ({e})")
        return {}


def fetch_media(account_id, token):
    print("  Fetching recent posts...", end=" ", flush=True)
    items = paginate(f"{account_id}/media", {
        "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink,thumbnail_url",
        "limit": 50,
    }, token, max_items=50)
    print(f"{len(items)} posts")
    return items


def fetch_post_insights(media_items, token):
    print(f"  Fetching insights for {len(media_items)} posts (may take ~{len(media_items)//3 + 1}s)...")
    results = {}
    for i, post in enumerate(media_items):
        mid = post["id"]
        mtype = post.get("media_type", "")
        metrics = "reach,saved,shares"
        if mtype == "REEL":
            metrics += ",plays"
        try:
            data = api_get(f"{mid}/insights", {"metric": metrics}, token)
            insight = {}
            for item in data.get("data", []):
                insight[item["name"]] = item.get("values", [{}])[0].get("value", item.get("value", 0))
            results[mid] = insight
        except RuntimeError:
            results[mid] = {}

        # progress dots every 5 posts
        if (i + 1) % 5 == 0:
            print(f"    {i + 1}/{len(media_items)} done...")

    print("  Post insights complete")
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\nSatori — fetching your Instagram data\n")

    config = load_config()
    token = config.get("meta", {}).get("token", "")
    account_id = config.get("meta", {}).get("account_id", "")

    if not token or token.startswith("EAA_PASTE"):
        print("❌  No token found in config.yaml.")
        print("    Add your Meta Graph API token under meta.token and try again.")
        sys.exit(1)

    if not account_id or "X" in str(account_id):
        print("❌  No account_id found in config.yaml.")
        print("    Add your Instagram Business Account ID under meta.account_id and try again.")
        sys.exit(1)

    print(f"Account: @{config.get('meta', {}).get('account_name', account_id)}\n")

    account = fetch_account(account_id, token)
    insights = fetch_account_insights(account_id, token)
    media = fetch_media(account_id, token)
    post_insights = fetch_post_insights(media, token)

    # Merge post insights into media items
    for post in media:
        post["insights"] = post_insights.get(post["id"], {})

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "account": account,
        "account_insights": insights,
        "media": media,
    }

    # Save snapshot
    Path("data").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(f"data/snapshot-{today}.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    # Summary
    followers = account.get("followers_count", "?")
    post_count = account.get("media_count", "?")
    print(f"\n✅  Done! Snapshot saved to {out_path}")
    print(f"\n   @{account.get('username', '')} · {followers:,} followers · {post_count} posts")
    print(f"   {len(media)} posts fetched with full insights\n")
    print("   Open Satori in Cowork — it will read from this snapshot automatically.\n")


if __name__ == "__main__":
    main()
