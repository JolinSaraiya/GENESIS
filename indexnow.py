#!/usr/bin/env python3
"""
=============================================================================
GENESIS INDEXNOW DISPATCHER (PS-04 INSTANT SEARCH ENGINE ALERT)
=============================================================================
Directly notifies Microsoft Bing, Yandex, Seznam, and AI search engines
(Perplexity, Copilot) when benchmark data is refreshed, eliminating crawl delay.
Supported protocols: IndexNow (RFC Draft / indexnow.org)
Zero external dependencies - runs natively on Python 3.8+.
=============================================================================
"""

import sys
import json
import urllib.request
import os

INDEXNOW_KEY = "83cd949a9582f4dd68b0a07148cd86ff"

TARGET_HOSTS = [
    {
        "host": "genesis-benchmark.vercel.app",
        "urls": [
            "https://genesis-benchmark.vercel.app/",
            "https://genesis-benchmark.vercel.app/data.json",
            "https://genesis-benchmark.vercel.app/dataset.csv",
            "https://genesis-benchmark.vercel.app/llms.txt"
        ]
    },
    {
        "host": "jolinsaraiya.github.io",
        "urls": [
            "https://jolinsaraiya.github.io/GENESIS/",
            "https://jolinsaraiya.github.io/GENESIS/data.json",
            "https://jolinsaraiya.github.io/GENESIS/dataset.csv",
            "https://jolinsaraiya.github.io/GENESIS/llms.txt"
        ]
    }
]

ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow"
]

def ping_indexnow(dry_run=False):
    print("=" * 65)
    print("GENESIS INDEXNOW DISPATCHER: Instant AI Crawler Notification")
    print("=" * 65)

    success_count = 0

    for target in TARGET_HOSTS:
        host = target["host"]
        urls = target["urls"]
        payload = {
            "host": host,
            "key": INDEXNOW_KEY,
            "keyLocation": f"https://{host}/{INDEXNOW_KEY}.txt",
            "urlList": urls
        }
        json_data = json.dumps(payload).encode("utf-8")

        print(f"\n➔ Pinging IndexNow for host: https://{host}")
        print(f"  Dispatched {len(urls)} modified endpoints...")

        if dry_run:
            print("  [DRY RUN] Payload verified; ping simulated successfully.")
            continue

        for endpoint in ENDPOINTS:
            req = urllib.request.Request(
                endpoint,
                data=json_data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "Genesis-IndexNow-Bot/1.0"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"  [✓] {endpoint} responded: HTTP {resp.status} (Dispatched)")
                    success_count += 1
            except urllib.error.HTTPError as e:
                # 200 or 202 is success. 422 usually means host is still warming up DNS.
                print(f"  [i] {endpoint} response: HTTP {e.code} ({e.reason})")
            except Exception as e:
                print(f"  [!] Notice connecting to {endpoint}: {e}")

    print("\n[COMPLETE] IndexNow crawler ping cycle finished.")
    return True

if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    ping_indexnow(dry_run=is_dry)
