from conftest import require_attr


def test_fetch_linkedin_job_urls_empty_result():
    """Method under test: integrations.linkedin_scraper.fetch_linkedin_job_urls"""
    fetch_linkedin_job_urls = require_attr("integrations.linkedin_scraper", "fetch_linkedin_job_urls")
    JobQuery = require_attr("domain.models", "JobQuery")
    query = JobQuery(keywords=["python"], location="berlin")
    urls = fetch_linkedin_job_urls(query)
    assert isinstance(urls, list)

