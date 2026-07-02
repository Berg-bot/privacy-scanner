# Privacy Scanner
A small command-line tool that scans a web page and reports on the third-party
domains it loads, flags known trackers, checks basic cookie/HTTPS hygiene, and
prints a simple privacy score.

This is a learning project inspired by tools like [DuckDuckGo's Tracker
Radar](https://github.com/duckduckgo/tracker-radar) — the idea is the same(find who's watching when you load a page), just at a much smaller,
educational scale. It only inspects the initial HTML response, so it won't catch trackers injected later by JavaScript — a real production tool
(including Tracker Radar itself) would use a headless browser to catch those too.

## What it does

- Fetches a URL and parses the returned HTML
- Collects every third-party domain referenced by `<script>`, `<img>`,
  `<iframe>`, and `<link>` tags
- Cross-references those domains against a small curated list of known
  trackers (analytics, advertising, social widgets, session recording)
- Checks whether the page is served over HTTPS
- Reports first-party cookies set on the initial response
- Calculates a simple 0–100 privacy score

## Installation

bash
- git clone https://github.com/Berg-bot/privacy-scanner.git
- cd privacy-scanner
- pip install -r requirements.txt


## Usage
bash
- python privacy_scanner.py https://example.com


Save the full report as JSON too:
- python privacy_scanner.py https://example.com --json report.json


### Example output

Privacy report for https://example.com
============================================================
HTTPS: yes
Third-party domains found: 4

Known trackers detected (2):
  - www.google-analytics.com  [Analytics]
  - connect.facebook.net  [Social]

All third-party domains contacted:
  - connect.facebook.net <- known tracker
  - fonts.googleapis.com
  - static.doubleclick.net <- known tracker
  - www.google-analytics.com <- known tracker

Cookies set on initial response (1):
  - session_id (secure)

Privacy score: 40 / 100
============================================================


## Running tests

bash
- python -m unittest test_scanner.py -v


## Limitations (on purpose — this is a portfolio project, not a product)

- Doesn't execute JavaScript, so dynamically-injected trackers are missed
- The tracker list in `trackers.py` is small and hand-curated, not
  automatically maintained
- The privacy score is a simple, transparent heuristic — not a rigorous
  methodology

## Possible next steps

- Use a headless browser (e.g. Playwright) to catch JS-injected trackers
- Pull in a real, maintained tracker list (e.g. EasyList or Tracker Radar)
- Check for fingerprinting scripts, not just known tracker domains
- Add a `--compare` mode to diff two scans of the same site over time
