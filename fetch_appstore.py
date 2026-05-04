#!/usr/bin/env python3
"""
Satori App Store Connect fetch helper
Run this once in Terminal before opening Satori:

    python fetch_appstore.py

Fetches your Apple App Store data and saves it to
data/snapshot-appstore-{today}.json. Satori reads from that file automatically.

Note: Sales reports are gzip-compressed TSV files — they cannot be fetched
directly by the Satori agent. This script is required for download/revenue data.
Ratings and reviews can also be fetched directly by the agent via WebFetch.
"""

import base64
import csv
import gzip
import io
import json
import sys
import time
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


def ensure_cryptography():
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
    except ImportError:
        print("Installing cryptography (one-time setup)...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "-q"])


def b64url(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(key_id, issuer_id, private_key_pem):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.backends import default_backend

    now = int(time.time())
    header = b64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}))
    payload = b64url(json.dumps({
        "iss": issuer_id,
        "iat": now,
        "exp": now + 1200,
        "aud": "appstoreconnect-v1",
    }))

    signing_input = f"{header}.{payload}".encode()
    private_key = serialization.load_pem_private_key(
        private_key_pem if isinstance(private_key_pem, bytes) else private_key_pem.encode(),
        password=None,
        backend=default_backend(),
    )
    signature = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    return f"{header}.{payload}.{b64url(signature)}"


# ── API helpers ───────────────────────────────────────────────────────────────

BASE = "https://api.appstoreconnect.apple.com/v1"


def api_get(path, token, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        errors = body.get("errors", [{}])
        detail = errors[0].get("detail", str(e)) if errors else str(e)
        raise RuntimeError(f"HTTP {e.code}: {detail}")


# ── Fetch routines ─────────────────────────────────────────────────────────────

def fetch_app_info(app_id, token):
    print("  Fetching app info...", end=" ", flush=True)
    try:
        result = api_get(f"apps/{app_id}", token, {
            "fields[apps]": "name,bundleId,primaryLocale",
        })
        print("done")
        return result.get("data", {})
    except RuntimeError as e:
        print(f"skipped ({e})")
        return {}


def fetch_reviews(app_id, token, max_items=100):
    print("  Fetching App Store reviews...", end=" ", flush=True)
    reviews = []
    try:
        data = api_get(f"apps/{app_id}/customerReviews", token, {
            "sort": "-createdDate",
            "limit": 50,
        })
        reviews.extend(data.get("data", []))
        next_url = data.get("links", {}).get("next")
        while next_url and len(reviews) < max_items:
            req = urllib.request.Request(next_url, headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            reviews.extend(data.get("data", []))
            next_url = data.get("links", {}).get("next")
        print(f"{len(reviews)} reviews")
        return reviews[:max_items]
    except RuntimeError as e:
        print(f"skipped ({e})")
        return []


def fetch_sales_reports(vendor_number, token, days=30):
    print(f"  Fetching sales reports (last {days} days)...")
    daily = []
    skipped = 0

    for i in range(days):
        date = (datetime.now() - timedelta(days=i + 1)).strftime("%Y-%m-%d")
        params = urllib.parse.urlencode({
            "filter[frequency]": "DAILY",
            "filter[reportDate]": date,
            "filter[reportType]": "SALES",
            "filter[vendorNumber]": vendor_number,
            "filter[reportSubType]": "SUMMARY",
        })
        url = f"https://api.appstoreconnect.apple.com/v1/salesReports?{params}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/a-gzip",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = gzip.decompress(resp.read())
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8")), delimiter="\t")
            day_units = 0
            day_proceeds = 0.0
            for row in reader:
                # Type 1 = new paid download, 1F = free download, 1T = re-download
                if row.get("Product Type Identifier", "") in ("1", "1F", "1T"):
                    try:
                        day_units += int(row.get("Units", 0) or 0)
                        day_proceeds += float(row.get("Developer Proceeds", 0) or 0)
                    except (ValueError, TypeError):
                        pass
            daily.append({"date": date, "units": day_units, "proceeds": round(day_proceeds, 2)})
        except urllib.error.HTTPError as e:
            if e.code == 404:
                skipped += 1  # report not generated yet (< 48h delay)
            else:
                print(f"    Skipped {date}: HTTP {e.code}")
        except Exception as e:
            print(f"    Skipped {date}: {e}")

        if (i + 1) % 10 == 0:
            print(f"    {i + 1}/{days} days processed...")

    total_units = sum(d["units"] for d in daily)
    total_proceeds = round(sum(d["proceeds"] for d in daily), 2)
    note = f" ({skipped} days pending — App Store reports have a 48h delay)" if skipped else ""
    print(f"  Sales done — {total_units:,} downloads · ${total_proceeds:,.2f} proceeds{note}")
    return {
        "days": list(reversed(daily)),
        "total_downloads": total_units,
        "total_proceeds": total_proceeds,
        "pending_days": skipped,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\nSatori — fetching your App Store data\n")

    config = load_config()
    asc = config.get("appstore", {})

    key_id = asc.get("key_id", "")
    issuer_id = asc.get("issuer_id", "")
    key_path = asc.get("key_path", "")
    app_apple_id = str(asc.get("app_apple_id", ""))
    vendor_number = str(asc.get("vendor_number", ""))

    missing = []
    if not key_id or key_id.startswith("X"): missing.append("appstore.key_id")
    if not issuer_id or issuer_id.startswith("x"): missing.append("appstore.issuer_id")
    if not key_path: missing.append("appstore.key_path")
    if not app_apple_id: missing.append("appstore.app_apple_id")

    if missing:
        print(f"❌  Missing config fields: {', '.join(missing)}")
        print("    See docs/appstore-setup.md for instructions.")
        sys.exit(1)

    p8_file = Path(key_path)
    if not p8_file.exists():
        print(f"❌  .p8 key file not found at: {key_path}")
        print("    Download it from App Store Connect (download is only possible once).")
        print("    Then update appstore.key_path in config.yaml and try again.")
        sys.exit(1)

    ensure_cryptography()

    with open(p8_file, "rb") as f:
        private_key_pem = f.read()

    app_name = asc.get("app_name", f"App {app_apple_id}")
    print(f"App: {app_name} (Apple ID: {app_apple_id})\n")

    print("  Generating App Store Connect JWT...", end=" ", flush=True)
    token = make_jwt(key_id, issuer_id, private_key_pem)
    print("OK\n")

    app_info = fetch_app_info(app_apple_id, token)
    reviews = fetch_reviews(app_apple_id, token)
    sales = fetch_sales_reports(vendor_number, token) if vendor_number else {}

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "platform": "appstore",
        "app": {"id": app_apple_id, "name": app_name, "info": app_info},
        "reviews": reviews,
        "sales_30d": sales,
    }

    Path("data").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(f"data/snapshot-appstore-{today}.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"\n✅  Done! Snapshot saved to {out_path}")
    print(f"\n   {app_name} · {len(reviews)} reviews fetched", end="")
    if sales:
        print(f" · {sales['total_downloads']:,} downloads · ${sales['total_proceeds']:,.2f} proceeds (30d)", end="")
    print("\n")
    print("   Open Satori — it will read from this snapshot automatically.\n")


if __name__ == "__main__":
    main()
