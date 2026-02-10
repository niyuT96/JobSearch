"""Job detail parsing entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .html_extractors import (
    extract_description_by_keywords,
    extract_json_ld_jobposting,
    extract_text_by_selector,
)


@dataclass(frozen=True)
class JobDetail:
    """Minimal parsed output (raw description)."""

    description: str


def parse_job_detail(
    html: str,
    site_type: str,
    keywords: Optional[List[str]],
    selector: Optional[str],
) -> JobDetail:
    """Dispatch extraction based on site type.

    Args:
        html: Raw HTML content.
        site_type: Site type (e.g., "generic", "json-ld").
        keywords: Optional keywords for generic extraction.
        selector: Optional CSS selector for generic extraction.

    Returns:
        JobDetail: Parsed description wrapper.

    Raises:
        ValueError: If site_type is unsupported or content not found.
    """

    if site_type == "generic":
        if selector:
            description = extract_text_by_selector(html, selector)
        else:
            description = extract_description_by_keywords(html, keywords or [])
    elif site_type == "json-ld":
        posting = extract_json_ld_jobposting(html)
        description = posting.get("description", "") if posting else ""
        if not description:
            raise ValueError("No JobPosting JSON-LD found in HTML.")
    else:
        raise ValueError(f"Unsupported site type: {site_type}")

    return JobDetail(description=description)
