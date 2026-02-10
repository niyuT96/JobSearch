"""Job de-duplication logic."""

from __future__ import annotations

from typing import List, Tuple

from domain.models import JobPosting


def deduplicate_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
    """Remove duplicates by (company, location, title).

    Args:
        jobs: List of JobPosting objects.

    Returns:
        List[JobPosting]: Deduplicated list in original order.
    """

    seen: set[Tuple[str, str, str]] = set()
    result: List[JobPosting] = []
    for job in jobs:
        key = (job.company_name.lower(), job.location.lower(), job.jobtitle.lower())
        if key in seen:
            continue
        seen.add(key)
        result.append(job)
    return result
