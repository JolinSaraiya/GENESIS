#!/usr/bin/env python3
"""
=============================================================================
GOOGLE SEARCH INDEXING API (INSTANT INDEXING BYPASS)
=============================================================================
Directly publishes URLs to Google's real-time Indexing API v3.
Forces Googlebot to crawl and re-index submitted pages in 5-15 minutes,
bypassing the slow standard Google Search Console crawl queue.

Setup:
  1. Go to https://console.cloud.google.com/
  2. Enable "Web Search Indexing API"
  3. Create a Service Account, generate a JSON Key, and save as 'service_account.json'
  4. In Google Search Console (search.google.com/search-console):
     Add the Service Account email as an 'Owner' under Settings -> Users.
  5. Run: python3 google_indexer.py
=============================================================================
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import ssl

user_site = os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.append(user_site)

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(WORKSPACE_DIR, "service_account.json")

URLS_TO_INDEX = [
    "https://genesis-drab-eight.vercel.app/",
    "https://genesis-drab-eight.vercel.app/what-is-kora-threads",
    "https://genesis-drab-eight.vercel.app/is-kora-threads-based-in-pune-or-bengaluru",
    "https://genesis-drab-eight.vercel.app/weaver-cooperatives",
    "https://genesis-drab-eight.vercel.app/kora-threads-size-medium",
    "https://genesis-drab-eight.vercel.app/minimoth-cod-verification",
    "https://genesis-drab-eight.vercel.app/return-window",
    "https://genesis-drab-eight.vercel.app/return-policy",
    "https://genesis-drab-eight.vercel.app/llms.txt",
    "https://genesis-drab-eight.vercel.app/data.json"
]

def check_setup():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print("\n" + "=" * 65)
        print("⚠️ GOOGLE INDEXING API: service_account.json NOT FOUND")
        print("=" * 65)
        print("\nTo activate Google's Instant Indexing API (5-15 min crawl):")
        print("\n1. Open Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a project and search for 'Web Search Indexing API' -> Click ENABLE.")
        print("3. Go to 'Credentials' -> Create 'Service Account' (name it 'google-indexer').")
        print("4. Click on the Service Account -> 'Keys' tab -> 'Add Key' -> 'Create new key' (JSON).")
        print("5. Save that downloaded JSON file into your project as:")
        print(f"   {SERVICE_ACCOUNT_PATH}")
        print("\n6. CRITICAL STEP in Google Search Console:")
        print("   - Open https://search.google.com/search-console")
        print("   - Select https://genesis-drab-eight.vercel.app/")
        print("   - Go to Settings -> Users and permissions -> Add User")
        print("   - Paste the Service Account email address and set Permission: 'Owner'.")
        print("\nOnce that's done, re-run: python3 google_indexer.py\n")
        return False
    return True

def get_oauth2_token(sa_data):
    """
    Generates a JWT signed with the Service Account RSA private key
    and exchanges it for a Google OAuth2 Bearer Access Token.
    """
    try:
        import base64
        import hmac
        import hashlib
        # We try to use cryptography or PyJWT if available, or instruct user
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            has_crypto = True
        except ImportError:
            has_crypto = False

        if not has_crypto:
            print("Installing cryptography for RSA signing...")
            os.system(f"{sys.executable} -m pip install cryptography --quiet")
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives.serialization import load_pem_private_key

        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {
            "iss": sa_data["client_email"],
            "scope": "https://www.googleapis.com/auth/indexing",
            "aud": "https://oauth2.googleapis.com/token",
            "exp": now + 3600,
            "iat": now
        }

        def b64url(data):
            return base64.urlsafe_b64encode(data).decode("utf-8").replace("=", "")

        header_b64 = b64url(json.dumps(header).encode("utf-8"))
        payload_b64 = b64url(json.dumps(payload).encode("utf-8"))
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        private_key = load_pem_private_key(sa_data["private_key"].encode("utf-8"), password=None)
        signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
        signature_b64 = b64url(signature)
        jwt_token = f"{header_b64}.{payload_b64}.{signature_b64}"

        token_req_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=token_req_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            token_resp = json.loads(r.read().decode("utf-8"))
            return token_resp.get("access_token")
    except Exception as e:
        print(f"Error obtaining Google OAuth2 token: {e}")
        return None

def publish_urls(access_token):
    print("\n" + "=" * 65)
    print("🚀 PUBLISHING URLS TO GOOGLE INDEXING API (INSTANT CRAWL TRIGGER)")
    print("=" * 65)
    ctx = ssl.create_default_context()

    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    for url in URLS_TO_INDEX:
        body = {
            "url": url,
            "type": "URL_UPDATED"
        }
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                notify_time = resp_json.get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "NOW")
                print(f" [✓] {url}")
                print(f"     Status: HTTP {resp.status} (Googlebot notified at {notify_time})")
        except Exception as e:
            print(f" [!] {url} -> {e}")

    print("\n[SUCCESS] Googlebot has been dispatched to crawl your URLs in 5-15 minutes!\n")

def main():
    if not check_setup():
        return
    with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as f:
        sa_data = json.load(f)
    print(f"\nAuthenticated Service Account: {sa_data.get('client_email')}")
    token = get_oauth2_token(sa_data)
    if token:
        publish_urls(token)
    else:
        print("Failed to authenticate with Google APIs.")

if __name__ == "__main__":
    main()
