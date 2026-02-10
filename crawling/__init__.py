"""Crawling utilities: site configs, URL building, and HTML fetching."""

from .site_registry import SiteConfig, detect_site  # noqa: F401
from .url_generator import build_search_urls  # noqa: F401
from .playwright_client import PlaywrightClient  # noqa: F401
