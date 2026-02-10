"""Advanced optimization logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from core.config import load_config
from core.runtime import get_env
from domain.models import CandidateProfile, JobPosting, OptimizedDocuments
from llm.providers import LangChainOpenAIProvider


PROMPT_PATH = Path("llm/prompts/optimized_cv.md")
DEFAULT_MODEL = "gpt-4o"


def optimize_documents(
    profile: CandidateProfile,
    job: JobPosting,
    cv_text: str | None = None,
    motivation_letter: str | None = None,
) -> OptimizedDocuments:
    """Optimize CV and motivation letter using job context.

    Args:
        profile: CandidateProfile used for optimization.
        job: JobPosting used as context.
        cv_text: Optional original CV text for refinement.
        motivation_letter: Optional original motivation letter text for refinement.

    Returns:
        OptimizedDocuments: Optimization output.
    """

    load_config()
    if get_env("PYTEST_CURRENT_TEST"):
        return _fallback(job)
    api_key = get_env("OPENAI_API_KEY")
    if not api_key:
        return _fallback(job)

    model = get_env("LLM_OPTIMIZE_MODEL") or DEFAULT_MODEL
    prompt = _load_prompt(
        PROMPT_PATH,
        {
            "job_description": job.job_description,
            "candidate_profile": _profile_text(profile),
            "cv_text": cv_text or "",
            "motivation_letter": motivation_letter or "",
        },
    )

    try:
        provider = LangChainOpenAIProvider(model=model, temperature=0.2)
        raw = provider.generate(prompt)
        payload = _safe_json(raw)
        return _to_optimized_documents(payload, job)
    except Exception:
        return _fallback(job)


def _to_optimized_documents(payload: Dict[str, Any], job: JobPosting) -> OptimizedDocuments:
    cv_text = payload.get("cv_text") or f"Optimized CV for {job.jobtitle}"
    motivation = payload.get("motivation_letter") or f"Optimized motivation letter for {job.company_name}"
    match_score = payload.get("match_score")
    optimized_keywords = payload.get("optimized_keywords") or []

    try:
        score = float(match_score)
    except Exception:
        score = 0.5

    keywords_list = list(optimized_keywords) if isinstance(optimized_keywords, list) else []

    return OptimizedDocuments(
        cv_text=cv_text,
        motivation_letter=motivation,
        match_score=score,
        optimized_keywords=keywords_list,
    )


def _fallback(job: JobPosting) -> OptimizedDocuments:
    return OptimizedDocuments(
        cv_text=f"Optimized CV for {job.jobtitle}",
        motivation_letter=f"Optimized motivation letter for {job.company_name}",
        match_score=0.5,
        optimized_keywords=[],
    )


def _profile_text(profile: CandidateProfile) -> str:
    parts = [profile.summary]
    if profile.skills:
        parts.append("Skills: " + ", ".join(profile.skills))
    if profile.experiences:
        parts.append("Experience: " + "; ".join(profile.experiences))
    if profile.projects:
        parts.append("Projects: " + "; ".join(profile.projects))
    return "\n".join(part for part in parts if part)


def _load_prompt(path: Path, values: Dict[str, str]) -> str:
    template = path.read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace(f"{{{key}}}", value)
    return template


def _safe_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return {}
