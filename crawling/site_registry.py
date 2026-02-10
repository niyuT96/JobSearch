"""Site registry and per-site crawl settings."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SiteConfig:
    """Configuration for a supported job site."""

    name: str
    follow_iframe: bool = False
    iframe_selector: str = "iframe"
    wait_jobposting: bool = False


SITE_CONFIGS = {
    "accso": SiteConfig(
        name="accso",
        follow_iframe=True,
        iframe_selector="iframe#jobFrame",
        wait_jobposting=False,
    ),
    "xing": SiteConfig(
        name="xing",
        follow_iframe=False,
        iframe_selector="iframe",
        wait_jobposting=True,
    ),
    "stepstone": SiteConfig(
        name="stepstone",
        follow_iframe=False,
        iframe_selector="iframe",
        wait_jobposting=True,
    ),
    "linkedin": SiteConfig(
        name="linkedin",
        follow_iframe=False,
        iframe_selector="iframe",
        wait_jobposting=False,
    ),
}


def detect_site(url: str) -> Optional[SiteConfig]:
    """Identify site configuration by URL.

    Returns None if the URL does not match a supported site.
    """

    if not url:
        return None
    lowered = url.lower()
    if "accso" in lowered:
        return SITE_CONFIGS["accso"]
    if "xing.com" in lowered:
        return SITE_CONFIGS["xing"]
    if "stepstone" in lowered:
        return SITE_CONFIGS["stepstone"]
    if "linkedin.com" in lowered:
        return SITE_CONFIGS["linkedin"]
    return None
