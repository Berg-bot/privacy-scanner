"""
Basic unit tests for privacy_scanner.py.

Run with:
    python -m unittest test_scanner.py -v
"""

import unittest

from privacy_scanner import find_third_party_domains, get_domain, score_privacy
from trackers import categorize

SAMPLE_HTML = """
<html>
<head>
    <script src="https://www.google-analytics.com/analytics.js"></script>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css">
</head>
<body>
    <img src="//static.doubleclick.net/pixel.gif">
    <img src="/local-image.png">
    <iframe src="https://connect.facebook.net/widget"></iframe>
    <script src="/local-script.js"></script>
</body>
</html>
"""


class TestGetDomain(unittest.TestCase):
    def test_basic_url(self):
        self.assertEqual(get_domain("https://example.com/page"), "example.com")

    def test_url_with_port(self):
        self.assertEqual(get_domain("http://example.com:8080/page"), "example.com")

    def test_invalid_url(self):
        self.assertIsNone(get_domain("not a url"))


class TestFindThirdPartyDomains(unittest.TestCase):
    def test_finds_external_domains_only(self):
        domains = find_third_party_domains(SAMPLE_HTML, base_domain="example.com")
        self.assertIn("www.google-analytics.com", domains)
        self.assertIn("fonts.googleapis.com", domains)
        self.assertIn("static.doubleclick.net", domains)
        self.assertIn("connect.facebook.net", domains)

    def test_excludes_local_resources(self):
        domains = find_third_party_domains(SAMPLE_HTML, base_domain="example.com")
        # local-image.png and local-script.js are relative paths, not full URLs
        self.assertEqual(len(domains), 4)


class TestCategorize(unittest.TestCase):
    def test_known_tracker_exact_match(self):
        self.assertEqual(categorize("doubleclick.net"), "Advertising")

    def test_known_tracker_subdomain_match(self):
        self.assertEqual(categorize("www.google-analytics.com"), "Analytics")

    def test_unknown_domain(self):
        self.assertIsNone(categorize("my-random-site.com"))


class TestScorePrivacy(unittest.TestCase):
    def test_perfect_score(self):
        self.assertEqual(score_privacy(tracker_count=0, total_third_party=0, https=True), 100)

    def test_https_penalty(self):
        self.assertEqual(score_privacy(tracker_count=0, total_third_party=0, https=False), 80)

    def test_tracker_penalty_caps(self):
        # Tracker penalty is capped at 60, so this shouldn't fall below 20
        # (100 - 60 tracker penalty - 20 https penalty = 20, not negative)
        self.assertEqual(score_privacy(tracker_count=20, total_third_party=20, https=False), 20)

    def test_score_never_negative(self):
        self.assertGreaterEqual(score_privacy(tracker_count=100, total_third_party=100, https=False), 0)


if __name__ == "__main__":
    unittest.main()
