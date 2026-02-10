"""Generate search URLs for supported job sites."""

from typing import Iterable, List
from urllib.parse import quote, urlencode


def _normalize_keywords(keywords: Iterable[str]) -> str:
    parts = [kw.strip() for kw in keywords if kw and kw.strip()]
    return " ".join(parts)


def _build_url(base: str, params: dict) -> str:
    cleaned = {k: v for k, v in params.items() if v is not None and v != ""}
    if not cleaned:
        return base
    return f"{base}?{urlencode(cleaned, doseq=True)}"


def _slugify(value: str) -> str:
    raw = "-".join(part for part in value.strip().lower().split() if part)
    return quote(raw, safe="-")


def build_search_urls(query) -> List[str]:
    """Build job board search URLs from a query object.

    This function is intentionally tolerant of the query type and uses
    attribute access to avoid tight coupling to the domain layer.
    """

    keywords = _normalize_keywords(getattr(query, "keywords", []) or [])
    location = (getattr(query, "location", "") or "").strip()
    urls = []

    # XING (no experience filter)
    urls.append(
        _build_url(
            "https://www.xing.com/jobs/search",
            {"keywords": keywords, "location": location},
        )
    )

    # StepStone (path-based search; no experience filter)
    stepstone_keywords = _slugify(keywords)
    stepstone_location = _slugify(location)
    urls.append(
        _build_url(
            f"https://www.stepstone.de/jobs/{stepstone_keywords}/in-{stepstone_location}",
            {"radius": 30, "searchOrigin": "Resultlist_top-search"},
        )
    )

    # LinkedIn (filters handled elsewhere; no experience filter here)
    urls.append(
        _build_url(
            "https://www.linkedin.com/jobs/search/",
            {"keywords": keywords, "location": location},
        )
    )

    # Accso (company site style search)
    accso_location_id = "2076"
    accso_location_map = {
        "darmstadt": "2076",
        "frankfurt": "2074",
    }
    if location and location.isdigit():
        accso_location_id = location
    elif location:
        accso_location_id = accso_location_map.get(location.lower(), accso_location_id)
    urls.append(
        _build_url(
            "https://accso.de/dabei-sein/jobs",
            {"jobs-overview-filter__locations": accso_location_id},
        )
    )

    return urls
