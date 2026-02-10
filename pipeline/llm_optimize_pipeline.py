"""Advanced LLM optimization pipeline."""

from __future__ import annotations

from typing import List

from domain.models import CandidateProfile, JobPosting, OptimizedDocuments
from llm.optimize_documents import optimize_documents


def run_llm_optimization(
    profile: CandidateProfile,
    jobs: List[JobPosting],
) -> List[OptimizedDocuments]:
    """Optimize CV and motivation letter for each job.

    Args:
        profile: CandidateProfile used for optimization.
        jobs: List of JobPosting objects.

    Returns:
        List[OptimizedDocuments]: Optimized outputs.
    """

    if not jobs:
        return []
    return [optimize_documents(profile, job) for job in jobs]
