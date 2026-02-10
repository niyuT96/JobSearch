from conftest import require_attr


def test_detect_site_known_url():
    """Method under test: crawling.site_registry.detect_site"""
    detect_site = require_attr("crawling.site_registry", "detect_site")
    config = detect_site("https://www.xing.com/jobs")
    assert config is not None

