from conftest import require_attr


def test_optimize_documents_returns_output():
    """Method under test: llm.optimize_documents.optimize_documents"""
    optimize_documents = require_attr("llm.optimize_documents", "optimize_documents")
    CandidateProfile = require_attr("domain.models", "CandidateProfile")
    JobPosting = require_attr("domain.models", "JobPosting")
    profile = CandidateProfile(summary="s", skills=["python"], experiences=[], projects=[])
    job = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="desc")
    result = optimize_documents(profile, job)
    assert result is not None

