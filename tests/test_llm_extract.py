from conftest import require_attr


def test_extract_job_fields_adds_fields():
    """Method under test: llm.extract_job_info.extract_job_fields"""
    extract_job_fields = require_attr("llm.extract_job_info", "extract_job_fields")
    JobPosting = require_attr("domain.models", "JobPosting")
    job = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="desc")
    result = extract_job_fields(job)
    assert result is not None

