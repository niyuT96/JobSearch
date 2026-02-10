"""JSON repository for job postings."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from domain.models import JobPosting


class JobRepository:
    """Save and load jobs as JSON."""

    def save_jobs(self, jobs: List[JobPosting], path: Path) -> None:
        """Persist data to JSON.

        Args:
            jobs: List of JobPosting objects.
            path: Output file path.
        """

        payload = [asdict(job) for job in jobs]
        Path(path).write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
