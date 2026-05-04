#!/usr/bin/env python3
"""
Satori Play Store fetch helper
Run this once in Terminal before opening Satori:

    python fetch_playstore.py

Fetches your Google Play Store data and saves it to
data/snapshot-playstore-{today}.json. Satori reads from that file automatically.
"""

import base64
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
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


def ensure_cryptography():
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError:
        print("Installing cryptography (one-time setup)...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "-q"])


def b64url(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(service_account):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend

    now = int(time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}))
    payload = b64url(json.dumps({
        "iss": service_account["client_email"],
        "scope": "https://www.googleapis.com/auth/androidpublisher https://www.googleapis.com/auth/playdeveloperreporting",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": now + 3600,
        "iat": now,
    }))

    signing_input = f"{header}.{payload}".encode()
    private_key = serialization.load_pem_private_key(
        service_account["private_key"].encode(),
        password=None,
        backend=default_backend(),
    )
    signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{header}.{payload}.{b64url(signature)}"


def get_access_token(jwt):
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        result = json.loads(e.read())

    if "error" in result:
        print(f"\n❌  Google auth failed: {result.get('error_description', result['error'])}")
        print("    Verify that the Android Publisher API is enabled in Google Cloud Console")
        print("    and that the service account has Play Console access (Setup > API access).")
        sys.exit(1)

    return result["access_token"]


# ── API helpers ───────────────────────────────────────────────────────────────

BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"


def api_get(path, token, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw)
            err = body.get("error", {})
            raise RuntimeError(f"HTTP {e.code}: {err.get('message', str(e))}")
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {raw.decode('utf-8', errors='replace')}")


# ── Fetch routines ─────────────────────────────────────────────────────────────

def fetch_app_details(pkg, token):
    # Android Publisher API has no public /details endpoint; rating is derived from reviews
    return {}


def fetch_reviews(pkg, token, max_items=100):
    print("  Fetching reviews...", end=" ", flush=True)
    reviews = []
    params = {"maxResults": 50}
    try:
        data = api_get(f"applications/{pkg}/reviews", token, params)
        reviews.extend(data.get("reviews", []))
        next_token = data.get("tokenPagination", {}).get("nextPageToken")
        while next_token and len(reviews) < max_items:
            params["token"] = next_token
            data = api_get(f"applications/{pkg}/reviews", token, params)
            reviews.extend(data.get("reviews", []))
            next_token = data.get("tokenPagination", {}).get("nextPageToken")
        print(f"{len(reviews)} reviews")
        return reviews[:max_items]
    except RuntimeError as e:
        print(f"skipped ({e})")
        return []


REPORTING_BASE = "https://playdeveloperreporting.googleapis.com/v1beta1"


def fetch_vitals(pkg, token, vital_type):
    label = "crash rate" if vital_type == "crashRate" else "ANR rate"
    metric = "crashRate7dUserWeighted" if vital_type == "crashRate" else "anrRate7dUserWeighted"
    print(f"  Fetching {label}...", end=" ", flush=True)
    url = f"{REPORTING_BASE}/apps/{urllib.parse.quote(pkg, safe='')}/{vital_type}MetricSet:query"
    from datetime import date, timedelta
    today = date.today() - timedelta(days=2)  # API has 2-day lag
    start = today - timedelta(days=30)
    body = json.dumps({
        "timelineSpec": {
            "aggregationPeriod": "DAILY",
            "startTime": {"year": start.year, "month": start.month, "day": start.day},
            "endTime": {"year": today.year, "month": today.month, "day": today.day},
        },
        "metrics": [metric],
        "pageSize": 30,
    }).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            print("done")
            return result
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            err_body = json.loads(raw)
            msg = err_body.get("error", {}).get("message", str(e))
        except json.JSONDecodeError:
            msg = raw.decode("utf-8", errors="replace")[:200]
        if e.code == 403:
            print("skipped (Play Console vitals permissions not granted — see docs/playstore-setup.md)")
        else:
            print(f"skipped (HTTP {e.code}: {msg})")
        return {}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\nSatori — fetching your Play Store data\n")

    config = load_config()
    ps = config.get("playstore", {})

    pkg = ps.get("package_name", "")
    key_path = ps.get("service_account_key_path", "")

    if not pkg or "example" in pkg:
        print("❌  No package_name set in config.yaml under playstore.")
        print("    Add your app's package name (e.g. com.yourcompany.app) and try again.")
        sys.exit(1)

    if not key_path:
        print("❌  No service_account_key_path set in config.yaml under playstore.")
        print("    See docs/playstore-setup.md for instructions.")
        sys.exit(1)

    key_file = Path(key_path)
    if not key_file.exists():
        print(f"❌  Service account key not found at: {key_path}")
        print("    Download it from Google Cloud Console and update config.yaml.")
        sys.exit(1)

    ensure_cryptography()

    with open(key_file) as f:
        service_account = json.load(f)

    app_name = ps.get("app_name", pkg)
    print(f"App: {app_name} ({pkg})\n")

    print("  Authenticating with Google...", end=" ", flush=True)
    jwt = make_jwt(service_account)
    token = get_access_token(jwt)
    print("OK\n")

    details = fetch_app_details(pkg, token)
    reviews = fetch_reviews(pkg, token)
    crash_vitals = fetch_vitals(pkg, token, "crashRate")
    anr_vitals = fetch_vitals(pkg, token, "anrRate")

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "platform": "playstore",
        "app": {"packageName": pkg, "name": app_name},
        "details": details,
        "reviews": reviews,
        "vitals": {
            "crash_rate": crash_vitals,
            "anr_rate": anr_vitals,
        },
    }

    Path("data").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(f"data/snapshot-playstore-{today}.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    ratings = [r["comments"][0]["userComment"]["starRating"] for r in reviews if r.get("comments")]
    avg_rating = f"{sum(ratings)/len(ratings):.1f}" if ratings else "?"
    print(f"\n✅  Done! Snapshot saved to {out_path}")
    print(f"\n   {app_name} · avg rating: {avg_rating} · {len(reviews)} reviews fetched\n")
    print("   Open Satori — it will read from this snapshot automatically.\n")


if __name__ == "__main__":
    main()
