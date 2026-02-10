"""Quick manual crawler test by URL or .env query.

Usage:
  python realTest.py "https://www.xing.com/jobs/..."
  python realTest.py

If no URL is provided, it will read JOB_KEYWORDS and JOB_LOCATION from .env
and generate search URLs.
"""

from __future__ import annotations

import sys

from core.config import load_config
from core.runtime import get_env
from crawling.playwright_client import PlaywrightClient
from crawling.site_registry import detect_site
from crawling.url_generator import build_search_urls
from domain.models import JobQuery


def _query_from_env() -> JobQuery:
    keywords_raw = get_env("JOB_KEYWORDS")
    location = get_env("JOB_LOCATION")
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
    return JobQuery(keywords=keywords, location=location)


def main() -> int:
    load_config()

    if len(sys.argv) >= 2:
        url = sys.argv[1]
        client = PlaywrightClient()
        site = detect_site(url)

        html = client.fetch(
            url,
            wait_for=None,
            wait_jobposting=site.wait_jobposting if site else False,
        )

        if site and site.follow_iframe:
            html = client.fetch_iframe(url, site.iframe_selector)

        print(html[:2000])
        return 0

    query = _query_from_env()
    urls = build_search_urls(query)
    for url in urls:
        print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
