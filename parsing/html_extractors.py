"""HTML extraction utilities."""

from __future__ import annotations

import json
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup


def extract_json_ld_jobposting(html: str) -> dict:
    """Find JobPosting JSON-LD in HTML.

    Args:
        html: Raw HTML content.

    Returns:
        dict: JobPosting JSON-LD object, or empty dict if not found.
    """

    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        text = script.get_text(strip=True)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        posting = _find_json_ld_jobposting(payload)
        if posting:
            return posting
    return {}


def extract_text_by_selector(html: str, selector: str) -> str:
    """Extract text from the first node matching a selector.

    Args:
        html: Raw HTML content.
        selector: CSS selector.

    Returns:
        str: Normalized text content.

    Raises:
        ValueError: If selector finds no node.
    """

    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(selector)
    if not node:
        raise ValueError(f"No element found for selector: {selector}")
    return _normalize_whitespace(node.get_text(" ", strip=True))


def extract_description_by_keywords(html: str, keywords: List[str]) -> str:
    """Extract description by scoring blocks with keywords.

    Args:
        html: Raw HTML content.
        keywords: List of keywords to match.

    Returns:
        str: Best matching text block.

    Raises:
        ValueError: If keywords are empty or no match found.
    """

    if not keywords or not any(kw.strip() for kw in keywords):
        raise ValueError("Keywords are required for generic extraction.")

    normalized_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
    soup = BeautifulSoup(html, "html.parser")
    candidates = soup.find_all(["main", "section", "article", "div"])

    best_text = ""
    best_score = 0
    for node in candidates:
        text = _normalize_whitespace(node.get_text(" ", strip=True))
        if not text:
            continue
        score = _keyword_score(text, normalized_keywords)
        if score > best_score:
            best_score = score
            best_text = text

    if not best_text:
        raise ValueError("No matching content found for the provided keywords.")
    return best_text


def _find_json_ld_jobposting(payload) -> Optional[dict]:
    if isinstance(payload, dict):
        if payload.get("@type") == "JobPosting":
            return payload
        for value in payload.values():
            found = _find_json_ld_jobposting(value)
            if found:
                return found
    if isinstance(payload, list):
        for item in payload:
            found = _find_json_ld_jobposting(item)
            if found:
                return found
    return None


def _keyword_score(text: str, keywords: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw in lowered)


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())
