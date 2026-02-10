from conftest import require_attr


def test_deduplicate_jobs_by_company_title_location():
    """Method under test: pipeline.job_dedup.deduplicate_jobs"""
    deduplicate_jobs = require_attr("pipeline.job_dedup", "deduplicate_jobs")
    JobPosting = require_attr("domain.models", "JobPosting")
    job1 = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="x")
    job2 = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="y")
    result = deduplicate_jobs([job1, job2])
    assert len(result) == 1


def test_deduplicate_jobs_keeps_distinct():
    """Method under test: pipeline.job_dedup.deduplicate_jobs"""
    deduplicate_jobs = require_attr("pipeline.job_dedup", "deduplicate_jobs")
    JobPosting = require_attr("domain.models", "JobPosting")
    job1 = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="x")
    job2 = JobPosting(company_name="B", jobtitle="Dev", location="Berlin", job_description="y")
    result = deduplicate_jobs([job1, job2])
    assert len(result) == 2

