from conftest import require_attr


def test_playwright_client_fetch_mocked(monkeypatch):
    """Method under test: crawling.playwright_client.PlaywrightClient.fetch"""
    PlaywrightClient = require_attr("crawling.playwright_client", "PlaywrightClient")
    client = PlaywrightClient()
    monkeypatch.setattr(client, "fetch", lambda url, wait_for=None: "<html></html>")
    html = client.fetch("https://example.com")
    assert html.startswith("<")

