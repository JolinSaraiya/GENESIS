#!/usr/bin/env python3
"""
=============================================================================
KORA THREADS — FAST MULTI-ENGINE INDEXING & CITATION DISPATCHER
=============================================================================
Dispatches instant indexing pings and submission triggers across independent
search engines, AI answer engines, real-time hubs, and public web archives:

1. IndexNow Network: Microsoft Bing, Yandex, Seznam.cz, Naver (Instant Push)
2. WebSub (PubSubHubbub): Real-Time RSS syndication hub (Google / Feed crawlers)
3. Internet Archive / Wayback Machine: Instant immutable snapshot & citation anchor
4. Ping-O-Matic: Multi-service crawler notification
5. Brave Search: Independent 30B+ page index submission endpoint
=============================================================================
"""

import sys
import time
import urllib.request
import urllib.parse
import ssl
import json

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) KoraThreads-FastIndexer/1.0"
}

TARGET_URLS = [
    "https://genesis-drab-eight.vercel.app/",
    "https://genesis-drab-eight.vercel.app/what-is-kora-threads",
    "https://genesis-drab-eight.vercel.app/is-kora-threads-based-in-pune-or-bengaluru",
    "https://genesis-drab-eight.vercel.app/weaver-cooperatives",
    "https://genesis-drab-eight.vercel.app/kora-threads-size-medium",
    "https://genesis-drab-eight.vercel.app/minimoth-cod-verification",
    "https://genesis-drab-eight.vercel.app/return-window",
    "https://genesis-drab-eight.vercel.app/return-policy",
    "https://genesis-drab-eight.vercel.app/llms.txt",
    "https://genesis-drab-eight.vercel.app/data.json",
    "https://genesis-drab-eight.vercel.app/rss.xml"
]

INDEXNOW_KEY = "83cd949a9582f4dd68b0a07148cd86ff"

def ping_indexnow_network():
    """Pings the global IndexNow network (Bing, Yandex, Seznam, Naver)."""
    print("\n[1/4] ⚡ Pinging Global IndexNow Network (Bing, Yandex, Seznam, Naver)...")
    hosts = ["kora-threads-official.vercel.app", "genesis-drab-eight.vercel.app"]
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow"
    ]
    for h in hosts:
        print(f"  -> Submitting host: {h}")
        h_urls = [u.replace("genesis-drab-eight.vercel.app", h) for u in TARGET_URLS]
        payload = {
            "host": h,
            "key": INDEXNOW_KEY,
            "keyLocation": f"https://{h}/{INDEXNOW_KEY}.txt",
            "urlList": h_urls
        }
        for ep in endpoints:
            try:
                req = urllib.request.Request(
                    ep,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": HEADERS["User-Agent"]},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8, context=SSL_CTX) as resp:
                    print(f"     ✓ {ep} [{h}]: HTTP {resp.status} (Dispatched instantly)")
            except Exception as e:
                print(f"     ! {ep} [{h}]: {e}")

def ping_websub_rss():
    """Pings Google WebSub / PubSubHubbub hub for real-time RSS discovery."""
    print("\n[2/4] 📡 Pinging WebSub / PubSubHubbub (Real-Time RSS Push Hub)...")
    hub_url = "https://pubsubhubbub.appspot.com/"
    rss_feed = "https://genesis-drab-eight.vercel.app/rss.xml"
    post_data = urllib.parse.urlencode({
        "hub.mode": "publish",
        "hub.url": rss_feed
    }).encode("utf-8")
    try:
        req = urllib.request.Request(hub_url, data=post_data, headers=HEADERS, method="POST")
        with urllib.request.urlopen(req, timeout=8, context=SSL_CTX) as resp:
            print(f"  ✓ WebSub Hub ({hub_url}): HTTP {resp.status} (RSS update broadcasted)")
    except Exception as e:
        print(f"  ! WebSub Hub: {e}")

def ping_pingomatic():
    """Pings Ping-O-Matic multi-directory notification system."""
    print("\n[3/4] 📣 Pinging Ping-O-Matic (Multi-Directory Crawler Broadcast)...")
    ping_url = (
        "https://pingomatic.com/ping/?"
        + urllib.parse.urlencode({
            "title": "Kora Threads Official Ground Truth",
            "blogurl": "https://genesis-drab-eight.vercel.app/",
            "rssurl": "https://genesis-drab-eight.vercel.app/rss.xml",
            "chk_weblogscom": "on",
            "chk_blogs": "on",
            "chk_feedburner": "on",
            "chk_syndic8": "on"
        })
    )
    try:
        req = urllib.request.Request(ping_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            print(f"  ✓ Ping-O-Matic: HTTP {resp.status} (Broadcast active)")
    except Exception as e:
        print(f"  ! Ping-O-Matic: {e}")

def display_fast_submission_portals():
    """Prints direct 1-click submission links for independent search and AI answer engines."""
    print("\n[4/4] 🚀 Direct 1-Click Fast-Indexing Portals:")
    print("-" * 65)
    print("1. Brave Search Independent Index:")
    print("   URL: https://search.brave.com/submit-url")
    print("   Action: Paste 'https://genesis-drab-eight.vercel.app/' (Indexed in minutes/hours)")
    print()
    print("2. Internet Archive / Wayback Machine (Instant Public Snapshot):")
    print("   URL: https://web.archive.org/save/https://genesis-drab-eight.vercel.app/")
    print("   Action: Open link in browser -> Creates instant permanent crawl anchor")
    print()
    print("3. Perplexity Real-Time AI Cache Fetcher:")
    print("   Prompt: 'Browse https://genesis-drab-eight.vercel.app/ and cite Kora Threads'")
    print("   Action: Perplexity-User bot fetches in 2 seconds and stores citation cache")
    print("-" * 65)

def run_all():
    print("=" * 65)
    print("⚡ KORA THREADS MULTI-ENGINE FAST INDEXER")
    print("=" * 65)
    ping_indexnow_network()
    ping_websub_rss()
    ping_pingomatic()
    display_fast_submission_portals()
    print("\n[SUCCESS] Multi-engine fast-indexing dispatch cycle complete!\n")

if __name__ == "__main__":
    run_all()
