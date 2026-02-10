import argparse
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
"""
Get fully rendered HTML from a webpage using Playwright.
"""

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch fully rendered HTML from a page using Playwright."
    )
    parser.add_argument("url", help="Target URL to open")
    parser.add_argument(
        "--output",
        default="rendered.html",
        help="Path to save the rendered HTML",
    )
    parser.add_argument(
        "--wait-for",
        dest="wait_for",
        help="CSS selector to wait for before snapshotting HTML",
    )
    parser.add_argument(
        "--site",
        choices=["accso", "xing", "stepstone", "linkedin"],
        help="Use a preset configuration for a known site",
    )
    parser.add_argument(
        "--wait-jobposting",
        action="store_true",
        help="Wait until a JobPosting JSON-LD script is present",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20000,
        help="Timeout in ms for navigation and waits",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run with a visible browser window",
    )
    parser.add_argument(
        "--follow-iframe",
        action="store_true",
        help="If an iframe is present, fetch the iframe src instead",
    )
    parser.add_argument(
        "--iframe-selector",
        default="iframe",
        help="CSS selector used to locate the iframe (default: iframe)",
    )
    return parser.parse_args()


def fetch_rendered_html(
    url: str,
    wait_for: Optional[str],
    timeout_ms: int,
    headless: bool,
    wait_jobposting: bool,
) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        page.set_default_timeout(timeout_ms)
        page.goto(url, wait_until="domcontentloaded")
        if wait_for:
            try:
                page.wait_for_selector(wait_for)
            except PlaywrightTimeoutError:
                pass
        if wait_jobposting:
            try:
                page.wait_for_function(
                    """() => {
                        const script = document.querySelector(
                            'script[type="application/ld+json"]'
                        );
                        return script && script.textContent.includes('"@type":"JobPosting"');
                    }"""
                )
            except PlaywrightTimeoutError:
                pass

        html = page.content()
        context.close()
        browser.close()

    return html


def extract_iframe_src(html: str, selector: str, base_url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.select_one(selector)
    if not iframe:
        return None
    src = iframe.get("src")
    if not src:
        return None
    return urljoin(base_url, src)


def main() -> int:
    args = parse_args()
    if not args.site:
        args.site = detect_site_from_url(args.url)
        if args.site and args.output == "rendered.html":
            args.output = default_output_for_site(args.site)
    if args.site:
        apply_site_preset(args)
    html = fetch_rendered_html(
        url=args.url,
        wait_for=args.wait_for,
        timeout_ms=args.timeout,
        headless=not args.headed,
        wait_jobposting=args.wait_jobposting,
    )
    if args.follow_iframe:
        iframe_url = extract_iframe_src(html, args.iframe_selector, args.url)
        if iframe_url:
            html = fetch_rendered_html(
                url=iframe_url,
                wait_for=args.wait_for,
                timeout_ms=args.timeout,
                headless=not args.headed,
                wait_jobposting=args.wait_jobposting,
            )
    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Saved rendered HTML to {args.output}")
    return 0


def apply_site_preset(args: argparse.Namespace) -> None:
    presets = {
        "accso": {
            "follow_iframe": True,
            "iframe_selector": "iframe#jobFrame",
        },
        "xing": {"wait_jobposting": True},
        "stepstone": {"wait_jobposting": True},
    }
    preset = presets.get(args.site)
    if not preset:
        return
    for key, value in preset.items():
        setattr(args, key, value)


def detect_site_from_url(url: str) -> Optional[str]:
    lowered = url.lower()
    if "accso" in lowered:
        return "accso"
    if "xing.com" in lowered:
        return "xing"
    if "stepstone" in lowered:
        return "stepstone"
    if "linkedin.com" in lowered:
        return "linkedin"
    return None


def default_output_for_site(site: str) -> str:
    outputs = {
        "accso": "full_iframe_accso.html",
        "xing": "rendered_Xing.html",
        "stepstone": "rendered_Stepstone.html",
        "linkedin": "rendered_LinkedIn.html",
    }
    return outputs.get(site, "rendered.html")


if __name__ == "__main__":
    #
    raise SystemExit(main())
