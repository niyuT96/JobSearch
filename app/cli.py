"""Application CLI entrypoints."""

from __future__ import annotations

import argparse
from typing import List

from core.config import load_config
from core.runtime import get_env
from domain.models import CandidateProfile, JobQuery
from pipeline.job_ingest_pipeline import (
    collect_job_listings,
    fetch_job_html,
    ingest_jobs,
    parse_job,
)
from llm.optimize_documents import optimize_documents


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments into a namespace.

    Args:
        None. Uses sys.argv implicitly via argparse.

    Returns:
        argparse.Namespace containing parsed arguments.

    Raises:
        SystemExit: If required arguments are missing or invalid.
    """

    parser = argparse.ArgumentParser(description="Run job search pipeline.")
    parser.add_argument("--keywords", required=True, help="Comma-separated keywords")
    parser.add_argument("--location", required=True, help="Location string")
    parser.add_argument("--limit", type=int, default=20, help="Max job links to return")
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Only print search URLs (do not fetch search pages)",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Fetch job pages and output optimized keywords",
    )
    parser.add_argument("--profile-summary", help="Candidate summary text")
    parser.add_argument("--profile-skills", help="Comma-separated skills")
    parser.add_argument("--profile-experiences", help="Comma-separated experiences")
    parser.add_argument("--profile-projects", help="Comma-separated projects")
    parser.add_argument("--cv-path", help="Path to CV PDF")
    parser.add_argument("--motivation-path", help="Path to motivation letter PDF")
    return parser.parse_args()


def run() -> int:
    """Execute the pipeline with CLI inputs.

    Returns:
        int: Process exit code (0 for success).

    Raises:
        SystemExit: Propagated from argparse when inputs are invalid.
    """

    load_config()
    args = parse_args()
    keywords = [kw.strip() for kw in args.keywords.split(",") if kw.strip()]
    query = JobQuery(keywords=keywords, location=args.location)

    if args.no_fetch:
        listings = ingest_jobs(query)
        for item in listings:
            print(item.url)
        return 0

    listings = collect_job_listings(query, limit=args.limit)
    if not listings:
        print("No job listings found from search pages.")
        print("Search URLs:")
        for item in ingest_jobs(query):
            print(item.url)
        return 0

    if not args.optimize:
        for item in listings:
            print(item.url)
        return 0

    profile = _build_profile(
        summary=args.profile_summary,
        skills=args.profile_skills,
        experiences=args.profile_experiences,
        projects=args.profile_projects,
    )
    cv_text = _read_pdf_text(args.cv_path or get_env("CV_PATH"))
    motivation_text = _read_pdf_text(args.motivation_path or get_env("MOTIVATION_LETTER_PATH"))

    for item in listings:
        html = fetch_job_html(item)
        posting = parse_job(html, None)
        optimized = optimize_documents(profile, posting, cv_text=cv_text, motivation_letter=motivation_text)
        keywords = ", ".join(optimized.optimized_keywords) if optimized.optimized_keywords else ""
        print(f"{item.url}\t{keywords}")

    return 0


def _split_list(value: str) -> List[str]:
    return [part.strip() for part in value.split(",") if part and part.strip()]


def _build_profile(
    summary: str | None,
    skills: str | None,
    experiences: str | None,
    projects: str | None,
) -> CandidateProfile:
    summary_text = summary or get_env("CANDIDATE_SUMMARY")
    skills_list = _split_list(skills or get_env("CANDIDATE_SKILLS"))
    exp_list = _split_list(experiences or get_env("CANDIDATE_EXPERIENCES"))
    proj_list = _split_list(projects or get_env("CANDIDATE_PROJECTS"))
    return CandidateProfile(
        summary=summary_text or "",
        skills=skills_list,
        experiences=exp_list,
        projects=proj_list,
    )


def _read_pdf_text(path: str) -> str:
    if not path:
        return ""
    try:
        import pdfplumber
    except Exception:
        return ""
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(text for text in pages if text.strip())
    except Exception:
        return ""
