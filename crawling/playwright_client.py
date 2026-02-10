"""Playwright-based HTML fetching with LinkedIn scraper fallback."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from core.runtime import get_env, run_async


@dataclass
class PlaywrightClient:
    """Encapsulate Playwright usage to fetch rendered HTML."""

    timeout_ms: int = 20000
    headless: bool = True

    def fetch(self, url: str, wait_for: Optional[str] = None, wait_jobposting: bool = False) -> str:
        """Return rendered HTML for a URL.

        Uses Playwright for most sites. For LinkedIn URLs, uses the
        joeyism/linkedin_scraper package (Playwright-based).
        """
        if "linkedin.com" in (url or "").lower():
            return self._fetch_linkedin_scraper(url)
        return self._fetch_playwright(url, wait_for=wait_for, wait_jobposting=wait_jobposting)

    def fetch_iframe(self, url: str, selector: str) -> str:
        """Follow iframe source and return iframe HTML."""

        html = self.fetch(url)
        iframe_url = extract_iframe_src(html, selector, url)
        if not iframe_url:
            raise ValueError(f"No iframe found for selector: {selector}")
        return self.fetch(iframe_url)

    def _fetch_playwright(self, url: str, wait_for: Optional[str], wait_jobposting: bool) -> str:
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise RuntimeError("Playwright is required to fetch non-LinkedIn pages.") from exc

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            page.set_default_timeout(self.timeout_ms)
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

    def _fetch_linkedin_scraper(self, url: str) -> str:
        """Fetch LinkedIn pages using joeyism/linkedin_scraper (Playwright).

        Requires:
        - pip install linkedin_scraper
        - playwright installed (linkedin_scraper depends on it)
        Optional login via env vars:
        - LINKEDIN_EMAIL
        - LINKEDIN_PASSWORD
        - LINKEDIN_COOKIE
        Optional session reuse:
        - LINKEDIN_SESSION_PATH (default: session.json)
        - LINKEDIN_SAVE_SESSION=1 to persist after login
        """

        try:
            from linkedin_scraper import (
                BrowserManager,
                JobScraper,
                load_credentials_from_env,
                login_with_cookie,
                login_with_credentials,
            )
        except Exception as exc:
            raise RuntimeError(
                "LinkedIn crawling requires linkedin_scraper and playwright."
            ) from exc

        async def _scrape() -> str:
            session_path = Path(get_env("LINKEDIN_SESSION_PATH") or "session.json")
            save_session = (get_env("LINKEDIN_SAVE_SESSION") or "").strip() == "1"

            async with BrowserManager(headless=self.headless) as browser:
                if session_path.exists():
                    await browser.load_session(str(session_path))

                page = browser.page
                email, password = load_credentials_from_env()
                cookie = get_env("LINKEDIN_COOKIE")

                if cookie:
                    await login_with_cookie(page, cookie)
                elif email and password:
                    await login_with_credentials(page, email, password)

                if save_session:
                    await browser.save_session(str(session_path))

                scraper = JobScraper(page)
                job = await scraper.scrape(url)
                description = getattr(job, "job_description", None)
                if description:
                    return description
                return await page.content()

        return run_async(_scrape())


def extract_iframe_src(html: str, selector: str, base_url: str) -> Optional[str]:
    """Extract iframe src from HTML and resolve to absolute URL."""

    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.select_one(selector)
    if not iframe:
        return None
    src = iframe.get("src")
    if not src:
        return None
    return urljoin(base_url, src)
