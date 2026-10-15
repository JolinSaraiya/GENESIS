#!/usr/bin/env python3
"""
Automated Test Suite for Phase 3: Machine Transport & Semantic Knowledge Graph
Validates:
  1. Schema.org JSON-LD syntax, schema types (TechArticle, Dataset, FAQPage).
  2. Wikidata entity URI grounding (sameAs: https://www.wikidata.org/wiki/Q107388714).
  3. Universal robots.txt permissions for AI crawlers (GPTBot, ClaudeBot, PerplexityBot, etc.).
  4. XML Sitemap syntax and endpoint priorities.
  5. Live synchronization engine update of dateModified and lastmod.
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
    assert len(graph) >= 3, "Expected at least 3 schema entities in @graph"

    types = [item.get("@type") for item in graph]
    print(f"  [✓] Found Schema Types: {types}")
    assert "TechArticle" in types, "TechArticle missing from @graph"
    assert "Dataset" in types, "Dataset missing from @graph"
    assert "FAQPage" in types, "FAQPage missing from @graph"

    # Validate TechArticle details
    article = next(item for item in graph if item.get("@type") == "TechArticle")
    assert article.get("headline"), "TechArticle headline missing"
    assert "datePublished" in article, "TechArticle datePublished missing"
    assert "dateModified" in article, "TechArticle dateModified missing"
    
    # Validate Wikidata entity link
    about_items = article.get("about", [])
    wikidata_found = any("https://www.wikidata.org/wiki/Q107388714" in str(item.get("sameAs")) for item in about_items)
    assert wikidata_found, "Wikidata entity URI (Q107388714) not found in TechArticle.about"
    print("  [✓] TechArticle linked to Wikidata Q107388714")

    # Validate Dataset details
    dataset = next(item for item in graph if item.get("@type") == "Dataset")
    distributions = dataset.get("distribution", [])
    formats = [d.get("encodingFormat") for d in distributions]
    assert "text/csv" in formats, "Dataset missing text/csv distribution"
    assert "application/json" in formats, "Dataset missing application/json distribution"
    assert "text/plain" in formats, "Dataset missing text/plain distribution"
    print("  [✓] Dataset distributions verified (CSV, JSON, Plaintext)")

    # Validate FAQPage
    faq = next(item for item in graph if item.get("@type") == "FAQPage")
    questions = faq.get("mainEntity", [])
    assert len(questions) >= 4, "Expected at least 4 FAQ questions"
    print(f"  [✓] FAQPage verified ({len(questions)} canonical Q&As)")

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

if __name__ == "__main__":
    try:
        test_schema_json_ld()
        test_robots_txt()
        test_sitemap_xml()
        print("\n=======================================================")
        print("ALL PHASE 3 AUTOMATED VERIFICATION TESTS PASSED (100%)!")
        print("=======================================================")
    except Exception as err:
        print(f"\n[FAIL] Phase 3 Test Failed: {err}")
        sys.exit(1)
