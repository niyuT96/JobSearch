from conftest import require_attr


def test_build_search_urls_basic():
    """Method under test: crawling.url_generator.build_search_urls"""
    build_search_urls = require_attr("crawling.url_generator", "build_search_urls")
    JobQuery = require_attr("domain.models", "JobQuery")
    query = JobQuery(keywords=["python"], location="berlin")
    urls = build_search_urls(query)
    assert isinstance(urls, list)
    assert all(isinstance(url, str) for url in urls)


def test_build_search_urls_empty_keywords():
    """Method under test: crawling.url_generator.build_search_urls"""
    build_search_urls = require_attr("crawling.url_generator", "build_search_urls")
    JobQuery = require_attr("domain.models", "JobQuery")
    query = JobQuery(keywords=[], location="berlin")
    urls = build_search_urls(query)
    assert isinstance(urls, list)


def test_build_search_urls_special_chars():
    """Method under test: crawling.url_generator.build_search_urls"""
    build_search_urls = require_attr("crawling.url_generator", "build_search_urls")
    JobQuery = require_attr("domain.models", "JobQuery")
    query = JobQuery(keywords=["c++", "data science"], location="New York")
    urls = build_search_urls(query)
    assert isinstance(urls, list)
    assert all(" " not in url for url in urls)

