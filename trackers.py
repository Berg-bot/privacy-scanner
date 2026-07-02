"""
A small, hand-curated list of well-known tracker domains, grouped by
category. This is NOT exhaustive -- real tools like DuckDuckGo's Tracker
Radar (https://github.com/duckduckgo/tracker-radar) crawl millions of
sites to build lists like this automatically. This file is just enough
to demonstrate the idea on a portfolio project.

Matching is done by suffix, so "www.google-analytics.com" matches the
"google-analytics.com" entry below.
"""

KNOWN_TRACKERS = {
    # Analytics
    "google-analytics.com": "Analytics",
    "googletagmanager.com": "Analytics",
    "hotjar.com": "Analytics",
    "mixpanel.com": "Analytics",
    "segment.io": "Analytics",
    "amplitude.com": "Analytics",

    # Advertising
    "doubleclick.net": "Advertising",
    "googlesyndication.com": "Advertising",
    "adsrvr.org": "Advertising",
    "criteo.com": "Advertising",
    "taboola.com": "Advertising",
    "outbrain.com": "Advertising",
    "amazon-adsystem.com": "Advertising",

    # Social widgets / trackers
    "facebook.net": "Social",
    "facebook.com": "Social",
    "connect.facebook.net": "Social",
    "twitter.com": "Social",
    "x.com": "Social",
    "linkedin.com": "Social",
    "pinterest.com": "Social",
    "tiktok.com": "Social",

    # Session replay / behavior tracking
    "fullstory.com": "Session Recording",
    "clarity.ms": "Session Recording",
    "mouseflow.com": "Session Recording",
}


def categorize(domain: str) -> str | None:
    """Return the tracker category for a domain, or None if not a known tracker."""
    domain = domain.lower()
    for tracker_domain, category in KNOWN_TRACKERS.items():
        if domain == tracker_domain or domain.endswith("." + tracker_domain):
            return category
    return None
