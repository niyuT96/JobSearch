"""Job ingestion pipeline: search -> crawl -> parse."""

from __future__ import annotations

from typing import Iterable, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from crawling.playwright_client import PlaywrightClient
from crawling.site_registry import SiteConfig, detect_site
from crawling.url_generator import build_search_urls
from domain.models import JobListing, JobPosting
from parsing.job_detail_parser import parse_job_detail


def ingest_jobs(query) -> List[JobListing]:
    """Generate search URLs and return JobListing objects.

    Args:
        query: JobQuery-like object.

    Returns:
        List[JobListing]: Listings for search pages.
    """

    listings: List[JobListing] = []
    urls = build_search_urls(query)
    for url in urls:
        site = detect_site(url)
        source = site.name if site else "unknown"
        listings.append(JobListing(url=url, source=source))
    return listings


def collect_job_listings(query, limit: int = 20) -> List[JobListing]:
    """Fetch search pages and extract job detail URLs.

    Args:
        query: JobQuery-like object.
        limit: Max number of job listings to return.

    Returns:
        List[JobListing]: Job detail page listings.
    """

    client = PlaywrightClient()
    results: List[JobListing] = []
    for search in ingest_jobs(query):
        site = detect_site(search.url)
        html = client.fetch(
            search.url,
            wait_for=None,
            wait_jobposting=site.wait_jobposting if site else False,
        )
        if site and site.follow_iframe:
            html = client.fetch_iframe(search.url, site.iframe_selector)
        for link in extract_listing_urls(html, search.url, site):
            results.append(JobListing(url=link, source=search.source))
            if len(results) >= limit:
                return results
    return results


def fetch_job_html(listing: JobListing) -> str:
    """Fetch HTML for a job listing URL.

    Args:
        listing: JobListing with URL.

    Returns:
        str: Rendered HTML.
    """

    client = PlaywrightClient()
    site = detect_site(listing.url)
    html = client.fetch(
        listing.url,
        wait_for=None,
        wait_jobposting=site.wait_jobposting if site else False,
    )
    if site and site.follow_iframe:
        html = client.fetch_iframe(listing.url, site.iframe_selector)
    return html


def parse_job(html: str, site: Optional[SiteConfig]) -> JobPosting:
    """Parse HTML into a JobPosting.

    Args:
        html: Raw HTML content.
        site: SiteConfig-like object.

    Returns:
        JobPosting: Structured job posting.
    """

    detail = parse_job_detail(html, "generic", keywords=["job"], selector=None)
    return JobPosting(
        company_name="Unknown",
        jobtitle="Unknown",
        location="Unknown",
        job_description=detail.description,
    )


def extract_listing_urls(html: str, base_url: str, site: Optional[SiteConfig]) -> List[str]:
    """Extract job detail URLs from a search page.

    Args:
        html: Raw HTML content.
        base_url: Search page URL used to resolve relative links.
        site: Detected SiteConfig, used to pick match rules.

    Returns:
        List[str]: Deduplicated list of job detail URLs.
    """

    soup = BeautifulSoup(html, "html.parser")
    urls: List[str] = []

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        if not href:
            continue
        full = urljoin(base_url, href)
        if _is_job_detail_url(full, site):
            if full not in urls:
                urls.append(full)
    return urls


def _is_job_detail_url(url: str, site: Optional[SiteConfig]) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if site and site.name == "linkedin":
        return "linkedin.com" in host and "/jobs/view/" in path
    if site and site.name == "stepstone":
        return "stepstone.de" in host and "/jobs/" in path and "/jobs/" in path
    if site and site.name == "xing":
        return "xing.com" in host and "/jobs/" in path
    if site and site.name == "accso":
        return "accso.de" in host and "/dabei-sein/jobs/" in path

    # Fallback heuristic
    return "/jobs/" in path
