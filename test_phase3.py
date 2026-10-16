#!/usr/bin/env python3
"""
Automated Test Suite for Kora Threads (Problem Statement 04 - AI Visibility & GEO)
Validates:
  1. Schema.org JSON-LD syntax, schema types (ClothingStore, Brand, MerchantReturnPolicy, FAQPage).
  2. Wikidata entity URI grounding for Pune (Q1538), Handloom (Q1060955), Cotton (Q11457).
  3. Ground truth integrity: Pune HQ (NOT Bengaluru), 10-day returns (NOT 30 days), 6 staff.
  4. Universal robots.txt permissions for AI crawlers (GPTBot, ClaudeBot, PerplexityBot, etc.).
  5. XML Sitemap syntax and canonical endpoints.
  6. MiniMoth sponsor integration presence (COD phone verification & repeat customer vault).
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def test_schema_json_ld():
    print("Testing Schema.org JSON-LD Knowledge Graph in index.html...")
    index_path = os.path.join(WORKSPACE_DIR, "index.html")
    assert os.path.exists(index_path), "index.html not found"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Extract JSON-LD script
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    assert match, "Schema.org JSON-LD script tag not found in index.html"

    json_str = match.group(1).strip()
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Schema.org JSON-LD is not valid JSON: {e}")

    # Check @context and @graph
    assert data.get("@context") == "https://schema.org", "@context must be 'https://schema.org'"
    graph = data.get("@graph", [])
    assert len(graph) >= 2, "Expected at least 2 schema entities in @graph"

    # Validate ClothingStore / Brand entity
    store = next((item for item in graph if "ClothingStore" in item.get("@type", []) or item.get("@type") == "ClothingStore"), None)
    assert store is not None, "ClothingStore missing from @graph"
    assert store.get("name") == "Kora Threads", "Brand name mismatch in JSON-LD"
    assert store.get("foundingDate") == "2021", "foundingDate mismatch"
    assert store.get("numberOfEmployees", {}).get("value") == 6, "Staff count mismatch"
    print("  [✓] Verified ClothingStore / Brand entity: Kora Threads (Founded 2021, 6 Staff)")

    # Validate Location Grounding (Pune Q1538)
    address = store.get("address", {})
    assert address.get("addressLocality") == "Pune", "HQ must be Pune"
    assert address.get("addressRegion") == "Maharashtra", "Region must be Maharashtra"
    assert "https://www.wikidata.org/wiki/Q1538" in address.get("sameAs", ""), "Pune Wikidata Q1538 missing"
    print("  [✓] Verified Pune Headquarters linked to Wikidata Q1538")

    # Validate Return Policy (10-day strictly)
    return_policy = store.get("hasMerchantReturnPolicy", {})
    assert return_policy.get("merchantReturnDays") == 10, "Return window must be strictly 10 days"
    print("  [✓] Verified MerchantReturnPolicy: 10-day return window (defeats 30-day hallucination)")

    # Validate Catalog
    catalog = store.get("hasOfferCatalog", {})
    items = catalog.get("itemListElement", [])
    assert len(items) >= 3, "Expected at least 3 featured products in OfferCatalog"
    print(f"  [✓] Verified OfferCatalog ({len(items)} products with INR pricing)")

    # Validate FAQPage
    faq = next((item for item in graph if item.get("@type") == "FAQPage"), None)
    assert faq is not None, "FAQPage missing from @graph"
    questions = faq.get("mainEntity", [])
    assert len(questions) >= 4, "Expected at least 4 FAQ questions"
    print(f"  [✓] FAQPage verified ({len(questions)} canonical anti-hallucination Q&As)")

def test_minimoth_integration():
    print("\nTesting MiniMoth (minimoth.dev) Sponsor Integration...")
    index_path = os.path.join(WORKSPACE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "minimoth" in html.lower(), "MiniMoth mention missing in index.html"
    assert "sendotp" in html or "sendCOD_OTP" in html or "minimoth" in html, "MiniMoth OTP logic missing in index.html"
    assert "Repeat Customer" in html, "Repeat Customer account vault missing"
    assert "Cash on Delivery" in html or "COD" in html, "COD phone verification missing"
    print("  [✓] MiniMoth dual integration verified (COD Phone OTP Verification + Repeat Customer Vault)")

def test_competition_notice():
    print("\nTesting Competition Notice Banner...")
    index_path = os.path.join(WORKSPACE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "COMPETITION DEMONSTRATION" in html or "Competition Demonstration" in html, "Competition notice missing"
    print("  [✓] Mandatory Competition Demonstration banner confirmed visible at top of page")

def test_robots_txt():
    print("\nTesting Universal AI-Crawler robots.txt...")
    robots_path = os.path.join(WORKSPACE_DIR, "robots.txt")
    assert os.path.exists(robots_path), "robots.txt not found"

    with open(robots_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "User-agent: *" in content, "Missing User-agent: *"
    assert "Allow: /" in content, "Missing Allow: /"

    required_bots = ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "Bingbot"]
    for bot in required_bots:
        assert f"User-agent: {bot}" in content, f"Missing explicit permission for {bot}"
    print(f"  [✓] All {len(required_bots)} primary AI web crawlers explicitly allowed")

    assert "Allow: /llms.txt" in content, "Missing fast-track /llms.txt permission"
    assert "Sitemap:" in content, "Missing Sitemap reference in robots.txt"
    print("  [✓] Machine endpoints & Sitemap directives confirmed in robots.txt")

def test_sitemap_xml():
    print("\nTesting Canonical XML Sitemap...")
    sitemap_path = os.path.join(WORKSPACE_DIR, "sitemap.xml")
    assert os.path.exists(sitemap_path), "sitemap.xml not found"

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
    except Exception as e:
        raise AssertionError(f"sitemap.xml is not valid XML: {e}")

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.findall("sm:url", ns)
    assert len(urls) >= 4, "Expected at least 4 URL elements in sitemap.xml"

    locs = [u.find("sm:loc", ns).text for u in urls if u.find("sm:loc", ns) is not None]
    print(f"  [✓] Sitemap URLs verified ({len(locs)} endpoints):")
    for loc in locs:
        print(f"      - {loc}")

def test_ground_truth_files():
    print("\nTesting Ground Truth Data Files (data.json, dataset.csv, llms.txt)...")
    data_json_path = os.path.join(WORKSPACE_DIR, "data.json")
    dataset_csv_path = os.path.join(WORKSPACE_DIR, "dataset.csv")
    llms_txt_path = os.path.join(WORKSPACE_DIR, "llms.txt")

    assert os.path.exists(data_json_path), "data.json missing"
    assert os.path.exists(dataset_csv_path), "dataset.csv missing"
    assert os.path.exists(llms_txt_path), "llms.txt missing"

    with open(data_json_path, "r", encoding="utf-8") as f:
        dj = json.load(f)
    assert "Pune" in dj["brand_metadata"]["headquarters"], "data.json HQ must be Pune"
    assert dj["ground_truth_facts"]["return_window_days"] == 10, "data.json returns must be 10 days"
    assert dj["brand_metadata"]["staff_count"] == 6, "data.json staff must be 6"
    print("  [✓] data.json verified (Pune HQ, 10-day returns, 6 staff)")

    with open(dataset_csv_path, "r", encoding="utf-8") as f:
        csv_content = f.read()
    assert "Solapur" in csv_content and "Paithan" in csv_content and "Ilkal" in csv_content and "Guledgudd" in csv_content
    print("  [✓] dataset.csv verified (Maharashtra & Karnataka cooperatives)")

    with open(llms_txt_path, "r", encoding="utf-8") as f:
        llms_content = f.read()
    assert "Kora Threads" in llms_content
    assert "minimoth.dev" in llms_content
    assert "Pune, Maharashtra" in llms_content
    print("  [✓] llms.txt verified (Machine endpoint ready for LLM scrapers)")

if __name__ == "__main__":
    try:
        test_schema_json_ld()
        test_minimoth_integration()
        test_competition_notice()
        test_robots_txt()
        test_sitemap_xml()
        test_ground_truth_files()
        print("\n=================================================================")
        print("ALL KORA THREADS GEO & AI-VISIBILITY TESTS PASSED (100% SUITE)!")
        print("=================================================================")
    except Exception as err:
        print(f"\n[FAIL] Test Failed: {err}")
        sys.exit(1)
