import argparse
import json
from pathlib import Path
from typing import Optional

import job_detail_parser as jdp
import playwright_fetch_html as pfh


SITE_CONFIG = {
    "accso": {
        "follow_iframe": True,
        "iframe_selector": "iframe#jobFrame",
        "wait_jobposting": False,
    },
    "xing": {
        "follow_iframe": False,
        "iframe_selector": "iframe",
        "wait_jobposting": True,
    },
    "stepstone": {
        "follow_iframe": False,
        "iframe_selector": "iframe",
        "wait_jobposting": True,
    },
    "linkedin": {
        "follow_iframe": False,
        "iframe_selector": "iframe",
        "wait_jobposting": False,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a job page and extract job info."
    )
    parser.add_argument("url", help="Job posting URL")
    parser.add_argument(
        "--output",
        help="Optional output HTML path for the rendered page",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write the rendered HTML to disk",
    )
    return parser.parse_args()


def detect_site(url: str) -> str:
    site = pfh.detect_site_from_url(url)
    if not site:
        raise ValueError("Unsupported site; cannot detect site from URL.")
    return site


def resolve_output(site: str, override: Optional[str]) -> Path:
    if override:
        return Path(override)
    return Path(pfh.default_output_for_site(site))


def fetch_html(url: str, site: str) -> str:
    config = SITE_CONFIG[site]
    html = pfh.fetch_rendered_html(
        url=url,
        wait_for=None,
        timeout_ms=20000,
        headless=True,
        wait_jobposting=config["wait_jobposting"],
    )
    if config["follow_iframe"]:
        iframe_url = pfh.extract_iframe_src(
            html,
            config["iframe_selector"],
            url,
        )
        if iframe_url:
            html = pfh.fetch_rendered_html(
                url=iframe_url,
                wait_for=None,
                timeout_ms=20000,
                headless=True,
                wait_jobposting=config["wait_jobposting"],
            )
    return html


def parse_result(html: str, site: str) -> str:
    if site in {"xing", "stepstone"}:
        posting = jdp.extract_jobposting_json_ld(html)
        if not posting:
            raise ValueError("No JobPosting JSON-LD found in HTML.")
        return json.dumps(posting, ensure_ascii=True, indent=2)
    if site == "accso":
        return jdp.extract_text_by_selector(html, ".step-stone-job-ad")
    if site == "linkedin":
        return jdp.extract_description_linkedin(html)
    raise ValueError(f"Unsupported site: {site}")


def main() -> int:
    args = parse_args()
    site = detect_site(args.url)
    output = resolve_output(site, args.output)

    html = fetch_html(args.url, site)
    if not args.no_save:
        output.write_text(html, encoding="utf-8")
    # Job information extraction
    result = parse_result(html, site)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
