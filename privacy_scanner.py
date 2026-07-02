#!/usr/bin/env python3
"""
privacy_scanner.py

A simple command-line tool that scans a web page and reports on the
third-party domains it loads, flags known trackers, checks basic cookie
and HTTPS behavior, and prints a lightweight privacy score.

This is a learning/portfolio project, not a production security tool.
It only looks at the initial HTML response -- it does not execute
JavaScript, so it will miss trackers that are injected dynamically.

Usage:
    python privacy_scanner.py https://example.com
    python privacy_scanner.py https://example.com --json report.json
"""

import argparse
import json
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from trackers import categorize

USER_AGENT = "privacy-scanner/0.1 (+https://github.com/berg-bot/privacy-scanner)"


def get_domain(url: str) -> str | None:
    """Extract the registrable-ish domain (netloc) from a URL."""
    try:
        netloc = urlparse(url).netloc
        return netloc.split(":")[0].lower() if netloc else None
    except Exception:
        return None


def fetch_page(url: str) -> requests.Response:
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response


def find_third_party_domains(html: str, base_domain: str) -> set[str]:
    """Find every external domain referenced by scripts, images, iframes, and links."""
    soup = BeautifulSoup(html, "html.parser")
    domains = set()

    tag_attrs = [
        ("script", "src"),
        ("img", "src"),
        ("iframe", "src"),
        ("link", "href"),
    ]

    for tag_name, attr in tag_attrs:
        for tag in soup.find_all(tag_name):
            src = tag.get(attr)
            if not src or not src.startswith(("http://", "https://", "//")):
                continue
            if src.startswith("//"):
                src = "https:" + src
            domain = get_domain(src)
            if domain and domain != base_domain:
                domains.add(domain)

    return domains


def check_cookies(response: requests.Response) -> list[dict]:
    """Summarize cookies set by the response (first-party, since JS-set cookies aren't visible here)."""
    cookies = []
    for cookie in response.cookies:
        cookies.append(
            {
                "name": cookie.name,
                "domain": cookie.domain,
                "secure": cookie.secure,
                "http_only": "HttpOnly" in str(cookie._rest.keys()) if hasattr(cookie, "_rest") else None,
            }
        )
    return cookies


def score_privacy(tracker_count: int, total_third_party: int, https: bool) -> int:
    """
    A deliberately simple scoring heuristic (0-100, higher is better).
    Real tools weigh dozens of signals -- this is just meant to be
    readable and easy to explain, not authoritative.
    """
    score = 100
    score -= min(tracker_count * 10, 60)          # known trackers hurt the most
    score -= min(max(total_third_party - tracker_count, 0) * 2, 20)  # other third parties, smaller penalty
    if not https:
        score -= 20
    return max(score, 0)


def scan(url: str) -> dict:
    base_domain = get_domain(url)
    if not base_domain:
        raise ValueError(f"Could not parse a domain from: {url}")

    response = fetch_page(url)
    third_party_domains = find_third_party_domains(response.text, base_domain)

    trackers_found = {}
    for domain in sorted(third_party_domains):
        category = categorize(domain)
        if category:
            trackers_found[domain] = category

    https = urlparse(response.url).scheme == "https"
    cookies = check_cookies(response)

    result = {
        "url": url,
        "final_url": response.url,
        "https": https,
        "third_party_domain_count": len(third_party_domains),
        "third_party_domains": sorted(third_party_domains),
        "known_trackers": trackers_found,
        "cookies_set": cookies,
        "privacy_score": score_privacy(len(trackers_found), len(third_party_domains), https),
    }
    return result


def print_report(result: dict) -> None:
    print(f"\nPrivacy report for {result['url']}")
    print("=" * 60)
    print(f"HTTPS: {'yes' if result['https'] else 'NO'}")
    print(f"Third-party domains found: {result['third_party_domain_count']}")

    if result["known_trackers"]:
        print(f"\nKnown trackers detected ({len(result['known_trackers'])}):")
        for domain, category in result["known_trackers"].items():
            print(f"  - {domain}  [{category}]")
    else:
        print("\nNo known trackers detected (from the curated list in trackers.py).")

    if result["third_party_domains"]:
        print(f"\nAll third-party domains contacted:")
        for domain in result["third_party_domains"]:
            flag = " <- known tracker" if domain in result["known_trackers"] else ""
            print(f"  - {domain}{flag}")

    if result["cookies_set"]:
        print(f"\nCookies set on initial response ({len(result['cookies_set'])}):")
        for cookie in result["cookies_set"]:
            secure_flag = "secure" if cookie["secure"] else "NOT secure"
            print(f"  - {cookie['name']} ({secure_flag})")

    print(f"\nPrivacy score: {result['privacy_score']} / 100")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Scan a web page for third-party trackers and basic privacy hygiene.")
    parser.add_argument("url", help="URL to scan, e.g. https://example.com")
    parser.add_argument("--json", metavar="FILE", help="Also write the full report as JSON to this file")
    args = parser.parse_args()

    try:
        result = scan(args.url)
    except requests.RequestException as exc:
        print(f"Error fetching {args.url}: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print_report(result)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Full report written to {args.json}")


if __name__ == "__main__":
    main()
