"""LinkedIn integration helpers.

This module is intentionally conservative about network calls. By default it
returns an empty list unless `LINKEDIN_SCRAPE=1` is set in the environment.
"""

from __future__ import annotations

from typing import List

from core.runtime import get_env, run_async


def fetch_linkedin_job_urls(query) -> List[str]:
    """Collect LinkedIn job URLs based on a search query.

    Args:
        query: JobQuery-like object with `keywords` and `location` attributes.

    Returns:
        A list of LinkedIn job URLs. Returns an empty list when scraping is
        disabled or if scraping fails.
    """

    search_url = _build_linkedin_search_url(query)
    if not search_url:
        return []

    if get_env("LINKEDIN_SCRAPE") != "1":
        return []

    try:
        return run_async(_scrape_job_urls(search_url))
    except Exception:
        return []


def _build_linkedin_search_url(query) -> str:
    """Build a LinkedIn search URL from a query object.

    Args:
        query: JobQuery-like object with `keywords` and `location` attributes.

    Returns:
        The LinkedIn search URL string, or an empty string if no inputs.
    """

    try:
        from crawling.url_generator import build_search_urls

        urls = build_search_urls(query)
        for url in urls:
            if "linkedin.com/jobs/search" in url:
                return url
    except Exception:
        pass

    return ""


async def _scrape_job_urls(search_url: str) -> List[str]:
    """Scrape LinkedIn job URLs from a search URL.

    Args:
        search_url: A LinkedIn search page URL.

    Returns:
        A list of job posting URLs, deduplicated.
    """

    from linkedin_scraper import (
        BrowserManager,
        JobSearchScraper,
        load_credentials_from_env,
        login_with_cookie,
        login_with_credentials,
    )

    async with BrowserManager() as browser:
        page = browser.page
        email, password = load_credentials_from_env()
        cookie = get_env("LINKEDIN_COOKIE")
        if cookie:
            await login_with_cookie(page, cookie)
        elif email and password:
            await login_with_credentials(page, email, password)

        scraper = JobSearchScraper(page)
        jobs = await scraper.scrape(search_url)

    urls: List[str] = []
    if jobs:
        for job in jobs:
            url = getattr(job, "linkedin_url", None)
            if url and url not in urls:
                urls.append(url)
    return urls
