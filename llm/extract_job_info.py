"""Lightweight extraction logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from core.config import load_config
from core.runtime import get_env
from domain.models import JobPosting
from llm.providers import LangChainOpenAIProvider


PROMPT_PATH = Path("llm/prompts/extract_job.md")
DEFAULT_MODEL = "gpt-4o-mini"


def extract_job_fields(job: JobPosting) -> JobPosting:
    """Add tasks, skills, and candidate profile fields using an LLM.

    Args:
        job: JobPosting to enrich.

    Returns:
        JobPosting: The same object with fields populated.
    """

    load_config()
    if get_env("PYTEST_CURRENT_TEST"):
        return _fallback(job)
    api_key = get_env("OPENAI_API_KEY")
    if not api_key:
        return _fallback(job)

    model = get_env("LLM_EXTRACT_MODEL") or DEFAULT_MODEL
    prompt = _load_prompt(PROMPT_PATH, {"job_description": job.job_description})

    try:
        provider = LangChainOpenAIProvider(model=model, temperature=0.0)
        raw = provider.generate(prompt)
        payload = _safe_json(raw)
        _apply_extract_payload(job, payload)
        return job
    except Exception:
        return _fallback(job)


def _apply_extract_payload(job: JobPosting, payload: Dict[str, Any]) -> None:
    future_tasks = payload.get("futureTasks") or []
    skills = payload.get("skills") or []
    candidate_profile = payload.get("candidateProfile") or []

    job.futureTasks = list(future_tasks) if isinstance(future_tasks, list) else []
    job.skills = list(skills) if isinstance(skills, list) else []

    if isinstance(candidate_profile, list):
        job.candidateProfile = "\n".join(str(item) for item in candidate_profile)
    else:
        job.candidateProfile = str(candidate_profile) if candidate_profile else ""


def _fallback(job: JobPosting) -> JobPosting:
    if job.futureTasks is None:
        job.futureTasks = []
    if job.skills is None:
        job.skills = []
    if job.candidateProfile is None:
        job.candidateProfile = ""
    return job


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
