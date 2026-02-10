"""Lightweight LLM extraction pipeline."""

from __future__ import annotations

from typing import List

from domain.models import JobPosting
from llm.extract_job_info import extract_job_fields


def run_llm_extraction(jobs: List[JobPosting]) -> List[JobPosting]:
    """Enrich jobs with tasks, skills, and candidate profile.

    Args:
        jobs: List of JobPosting objects.

    Returns:
        List[JobPosting]: Enriched job postings.
    """

    if not jobs:
        return []
    return [extract_job_fields(job) for job in jobs]
