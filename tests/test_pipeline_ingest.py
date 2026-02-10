from conftest import require_attr


def test_ingest_jobs_returns_listings():
    """Method under test: pipeline.job_ingest_pipeline.ingest_jobs"""
    ingest_jobs = require_attr("pipeline.job_ingest_pipeline", "ingest_jobs")
    JobQuery = require_attr("domain.models", "JobQuery")
    JobListing = require_attr("domain.models", "JobListing")

    query = JobQuery(keywords=["python"], location="berlin")
    jobs = ingest_jobs(query)
    assert isinstance(jobs, list)
    assert all(isinstance(item, JobListing) for item in jobs)
