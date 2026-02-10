"""Core domain models for job search and optimization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JobQuery:
    """Encapsulate search parameters (keywords, location)."""

    keywords: List[str]
    location: str

    def __post_init__(self) -> None:
        self.keywords = [kw.strip() for kw in (self.keywords or []) if kw and kw.strip()]
        self.location = (self.location or "").strip()


@dataclass
class JobListing:
    """Represent a job listing with URL and source site."""

    url: str
    source: str

    def __post_init__(self) -> None:
        self.url = (self.url or "").strip()
        self.source = (self.source or "").strip()
        if not self.url:
            raise ValueError("JobListing.url is required.")
        if not self.source:
            raise ValueError("JobListing.source is required.")


@dataclass
class JobPosting:
    """Structured job details after parsing and LLM extraction."""

    company_name: str
    jobtitle: str
    location: str
    job_description: str
    futureTasks: List[str] = field(default_factory=list)
    candidateProfile: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    matchScore: Optional[float] = None
    optimizedKeywords: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.company_name = (self.company_name or "").strip()
        self.jobtitle = (self.jobtitle or "").strip()
        self.location = (self.location or "").strip()
        self.job_description = (self.job_description or "").strip()
        if not self.company_name:
            raise ValueError("JobPosting.company_name is required.")
        if not self.jobtitle:
            raise ValueError("JobPosting.jobtitle is required.")
        if not self.location:
            raise ValueError("JobPosting.location is required.")
        if not self.job_description:
            raise ValueError("JobPosting.job_description is required.")


@dataclass
class CandidateProfile:
    """User profile data used for optimization."""

    summary: str
    skills: List[str]
    experiences: List[str]
    projects: List[str]

    def __post_init__(self) -> None:
        self.summary = (self.summary or "").strip()
        self.skills = [s.strip() for s in (self.skills or []) if s and s.strip()]
        self.experiences = [e.strip() for e in (self.experiences or []) if e and e.strip()]
        self.projects = [p.strip() for p in (self.projects or []) if p and p.strip()]


@dataclass
class OptimizedDocuments:
    """Optimized CV and motivation letter plus match score."""

    cv_text: str
    motivation_letter: str
    match_score: float
    optimized_keywords: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.cv_text = (self.cv_text or "").strip()
        self.motivation_letter = (self.motivation_letter or "").strip()
        if not self.cv_text:
            raise ValueError("OptimizedDocuments.cv_text is required.")
        if not self.motivation_letter:
            raise ValueError("OptimizedDocuments.motivation_letter is required.")
        if not (0.0 <= float(self.match_score) <= 1.0):
            raise ValueError("OptimizedDocuments.match_score must be between 0.0 and 1.0.")
