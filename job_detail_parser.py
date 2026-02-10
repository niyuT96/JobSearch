import argparse
import json
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class JobDetail:
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract job description from a saved HTML file."
    )
    parser.add_argument("input", help="Path to the saved HTML file")
    parser.add_argument(
        "--site",
        choices=["linkedin", "json-ld", "generic", "xing", "stepstone", "accso"],
        default="generic",
        help="Site type to use for parsing",
    )
    parser.add_argument(
        "--keywords",
        help="Comma-separated keywords used for generic extraction",
    )
    parser.add_argument(
        "--selector",
        help="CSS selector used for generic extraction",
    )
    parser.add_argument(
        "--output",
        choices=["description", "json-ld"],
        default="description",
        help="Select output mode",
    )
    return parser.parse_args()


def parse_job_detail(
    html: str,
    site_type: str,
    keywords: Optional[List[str]],
    selector: Optional[str],
) -> JobDetail:
    """Dispatch extraction based on site type."""
    if site_type == "linkedin":
        description = extract_description_linkedin(html)
    elif site_type == "json-ld":
        description = extract_description_json_ld(html)
    elif site_type == "generic":
        if selector:
            description = extract_text_by_selector(html, selector)
        else:
            description = extract_description_by_keywords(html, keywords or [])
    else:
        raise ValueError(f"Unsupported site type: {site_type}")

    return JobDetail(description=description)


def extract_description_linkedin(html: str) -> str:
    """Extract LinkedIn JobPosting description from embedded JSON in <code>."""
    payload = load_payload_from_html(html)
    job = find_job_posting(payload)
    if not job:
        raise ValueError("No LinkedIn JobPosting entity found in payload.")
    return (job.get("description") or {}).get("text", "")


def load_payload_from_html(html: str) -> dict:
    """Extract the first JSON payload that contains a JobPosting entity."""
    soup = BeautifulSoup(html, "html.parser")
    payloads: List[dict] = []
    for code in soup.find_all("code"):
        text = unescape(code.get_text(strip=True))
        if not text.startswith("{"):
            continue
        try:
            payloads.append(json.loads(text))
        except json.JSONDecodeError:
            continue

    for payload in payloads:
        if find_job_posting(payload):
            return payload

    raise ValueError("No JSON payload with a JobPosting entity found in <code> tags.")


def find_job_posting(payload: dict) -> Optional[dict]:
    """Locate the JobPosting entity by recursively walking the payload."""
    direct = _find_job_posting_in_node(payload.get("included", []))
    if direct:
        return direct
    return _find_job_posting_in_node(payload)


def _find_job_posting_in_node(node) -> Optional[dict]:
    """Depth-first search for a JobPosting entity in a nested structure."""
    if isinstance(node, dict):
        if node.get("$type") == "com.linkedin.voyager.dash.jobs.JobPosting":
            return node
        for value in node.values():
            found = _find_job_posting_in_node(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_job_posting_in_node(item)
            if found:
                return found
    return None


def extract_description_json_ld(html: str) -> str:
    """Extract JobPosting description from JSON-LD (schema.org)."""
    posting = extract_jobposting_json_ld(html)
    if posting and posting.get("description"):
        return _strip_html(posting.get("description", ""))

    raise ValueError("No JobPosting JSON-LD found in HTML.")


def extract_jobposting_json_ld(html: str) -> dict:
    """Return the JobPosting JSON-LD object if present."""
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


def _find_json_ld_jobposting(payload) -> Optional[dict]:
    if isinstance(payload, dict):
        if payload.get("@type") == "JobPosting":
            return payload
        for value in payload.values():
            found = _find_json_ld_jobposting(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = _find_json_ld_jobposting(item)
            if found:
                return found
    return None


def extract_description_by_keywords(html: str, keywords: List[str]) -> str:
    """Extract description by locating the best text block matching keywords."""
    if not keywords:
        raise ValueError("Keywords are required for generic extraction.")

    normalized_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
    if not normalized_keywords:
        raise ValueError("Keywords are required for generic extraction.")

    soup = BeautifulSoup(html, "html.parser")
    candidates = soup.find_all(["main", "section", "article", "div"])  # broad scope

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


def extract_text_by_selector(html: str, selector: str) -> str:
    """Extract text from the first node matching the selector."""
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(selector)
    if not node:
        raise ValueError(f"No element found for selector: {selector}")
    return _normalize_whitespace(node.get_text(" ", strip=True))


def _keyword_score(text: str, keywords: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw in lowered)


def _strip_html(value: str) -> str:
    return _normalize_whitespace(BeautifulSoup(value, "html.parser").get_text(" ", strip=True))


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    args = parse_args()
    if args.site in {"linkedin", "xing", "stepstone", "accso"}:
        apply_preset(args)
    html = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    keywords = args.keywords.split(",") if args.keywords else None
    if args.output == "json-ld":
        posting = extract_jobposting_json_ld(html)
        if not posting:
            raise ValueError("No JobPosting JSON-LD found in HTML.")
        print(json.dumps(posting, ensure_ascii=True, indent=2))
        return 0

    detail = parse_job_detail(html, args.site, keywords, args.selector)
    print(detail.description)
    return 0


def apply_preset(args: argparse.Namespace) -> None:
    presets = {
        "linkedin": {"site": "linkedin", "output": "description"},
        "xing": {"site": "json-ld", "output": "json-ld"},
        "stepstone": {"site": "json-ld", "output": "json-ld"},
        "accso": {"site": "generic", "selector": ".step-stone-job-ad"},
    }
    preset = presets.get(args.site)
    if not preset:
        return
    for key, value in preset.items():
        setattr(args, key, value)


if __name__ == "__main__":
    # python job_detail_parser.py "rendered_XING.html" --site xing
    # python job_detail_parser.py "rendered_Stepstone.html" --site stepstone
    # python job_detail_parser.py "full_iframe.html" --site accso
    # python job_detail_parser.py "TestLinkedIn.html" --site linkedin
    raise SystemExit(main())
