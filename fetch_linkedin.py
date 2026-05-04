#!/usr/bin/env python3
"""
Satori LinkedIn fetch helper
Run this once in Terminal before opening Satori:

    python fetch_linkedin.py

Fetches your LinkedIn Company Page data and saves it to
data/snapshot-linkedin-{today}.json. Satori reads from that file automatically.

Note: LinkedIn access tokens expire every 60 days. If this script fails with a
401 error, refresh your token — see docs/linkedin-setup.md.
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path


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
        print("    Open Satori in Claude Code first to complete setup.")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


# ── API helpers ───────────────────────────────────────────────────────────────

BASE = "https://api.linkedin.com/v2"


def api_get(path, token, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": "202312",
        "X-Restli-Protocol-Version": "2.0.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read())
        except Exception:
            pass
        msg = body.get("message", str(e))
        if e.code == 401:
            print(f"\n❌  LinkedIn token expired or invalid (401).")
            print("    Refresh your access token at https://www.linkedin.com/developers/apps")
            print("    Then update linkedin.access_token in config.yaml and try again.")
            sys.exit(1)
        if e.code == 403:
            raise RuntimeError(f"HTTP 403 — missing permission: {msg}")
        raise RuntimeError(f"HTTP {e.code}: {msg}")


# ── Fetch routines ─────────────────────────────────────────────────────────────

def fetch_org_info(org_id, token):
    print("  Fetching organization info...", end=" ", flush=True)
    try:
        result = api_get(f"organizations/{org_id}", token, {
            "projection": "(id,name,localizedName,followerCount,vanityName,description)"
        })
        print("done")
        return result
    except RuntimeError as e:
        print(f"skipped ({e})")
        return {}


def fetch_follower_stats(org_id, token):
    print("  Fetching follower statistics...", end=" ", flush=True)
    org_urn = f"urn:li:organization:{org_id}"
    try:
        result = api_get("organizationalEntityFollowerStatistics", token, {
            "q": "organizationalEntity",
            "organizationalEntity": org_urn,
        })
        print("done")
        return result.get("elements", [])
    except RuntimeError as e:
        print(f"skipped ({e})")
        return []


def fetch_share_statistics(org_id, token, days=30):
    print(f"  Fetching share/engagement statistics (last {days} days)...", end=" ", flush=True)
    org_urn = f"urn:li:organization:{org_id}"
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    since_ms = now_ms - days * 24 * 3600 * 1000
    try:
        result = api_get("organizationalEntityShareStatistics", token, {
            "q": "organizationalEntity",
            "organizationalEntity": org_urn,
            "timeIntervals.timeGranularityType": "DAY",
            "timeIntervals.timeRange.start": since_ms,
            "timeIntervals.timeRange.end": now_ms,
        })
        print("done")
        return result.get("elements", [])
    except RuntimeError as e:
        print(f"skipped ({e})")
        return []


def fetch_posts(org_id, token, count=20):
    print(f"  Fetching recent posts...", end=" ", flush=True)
    org_urn = urllib.parse.quote(f"urn:li:organization:{org_id}", safe="")
    try:
        result = api_get("ugcPosts", token, {
            "q": "authors",
            "authors": f"List(urn:li:organization:{org_id})",
            "count": count,
            "sortBy": "LAST_MODIFIED",
        })
        posts = result.get("elements", [])
        print(f"{len(posts)} posts")
        return posts
    except RuntimeError as e:
        print(f"skipped ({e})")
        return []


def fetch_post_stats(org_id, posts, token):
    if not posts:
        return {}
    print(f"  Fetching stats for {len(posts)} posts...", end=" ", flush=True)
    org_urn = f"urn:li:organization:{org_id}"
    post_urns = [p["id"] for p in posts if "id" in p]
    if not post_urns:
        print("skipped (no post IDs)")
        return {}

    # LinkedIn allows batch stats via shares=List(...) — up to 20 at a time
    stats = {}
    for i in range(0, len(post_urns), 20):
        batch = post_urns[i:i + 20]
        shares_param = "List(" + ",".join(urllib.parse.quote(u, safe="") for u in batch) + ")"
        try:
            result = api_get("organizationalEntityShareStatistics", token, {
                "q": "organizationalEntity",
                "organizationalEntity": org_urn,
                "shares": shares_param,
            })
            for el in result.get("elements", []):
                share_urn = el.get("share") or el.get("ugcPost", "")
                if share_urn:
                    stats[share_urn] = el.get("totalShareStatistics", {})
        except RuntimeError:
            pass

    print("done")
    return stats


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\nSatori — fetching your LinkedIn data\n")

    config = load_config()
    li = config.get("linkedin", {})

    token = li.get("access_token", "")
    org_id = str(li.get("org_id", ""))

    if not token or token.startswith("AQX_PASTE"):
        print("❌  No access token found in config.yaml under linkedin.access_token.")
        print("    See docs/linkedin-setup.md for instructions.")
        sys.exit(1)

    if not org_id:
        print("❌  No org_id found in config.yaml under linkedin.org_id.")
        print("    See docs/linkedin-setup.md to find your Company Page ID.")
        sys.exit(1)

    org_name = li.get("org_name", f"Org {org_id}")
    print(f"Page: {org_name} (org ID: {org_id})\n")

    org_info = fetch_org_info(org_id, token)
    follower_stats = fetch_follower_stats(org_id, token)
    share_stats = fetch_share_statistics(org_id, token)
    posts = fetch_posts(org_id, token)
    post_stats = fetch_post_stats(org_id, posts, token)

    # Attach per-post stats
    for post in posts:
        post_id = post.get("id", "")
        post["stats"] = post_stats.get(post_id, {})

    # Compute 30-day aggregate engagement from share_stats
    total_impressions = sum(
        el.get("totalShareStatistics", {}).get("impressionCount", 0)
        for el in share_stats
    )
    total_clicks = sum(
        el.get("totalShareStatistics", {}).get("clickCount", 0)
        for el in share_stats
    )
    total_reactions = sum(
        el.get("totalShareStatistics", {}).get("likeCount", 0)
        for el in share_stats
    )
    total_comments = sum(
        el.get("totalShareStatistics", {}).get("commentCount", 0)
        for el in share_stats
    )
    total_shares = sum(
        el.get("totalShareStatistics", {}).get("shareCount", 0)
        for el in share_stats
    )

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "platform": "linkedin",
        "org": {
            "id": org_id,
            "name": org_name,
            "info": org_info,
        },
        "follower_stats": follower_stats,
        "share_stats_30d": {
            "daily": share_stats,
            "totals": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "reactions": total_reactions,
                "comments": total_comments,
                "shares": total_shares,
            },
        },
        "posts": posts,
    }

    Path("data").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(f"data/snapshot-linkedin-{today}.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    followers = org_info.get("followerCount", "?")
    print(f"\n✅  Done! Snapshot saved to {out_path}")
    print(f"\n   {org_name} · {followers:,} followers · {len(posts)} posts fetched")
    if total_impressions:
        print(f"   {total_impressions:,} impressions · {total_reactions:,} reactions (last 30 days)")
    print("\n   Open Satori — it will read from this snapshot automatically.\n")


if __name__ == "__main__":
    main()
