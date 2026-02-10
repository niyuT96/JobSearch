from conftest import require_attr


def test_domain_models_basic_construction():
    """Methods under test: domain.models.JobQuery, JobListing, JobPosting, CandidateProfile, OptimizedDocuments"""
    JobQuery = require_attr("domain.models", "JobQuery")
    JobListing = require_attr("domain.models", "JobListing")
    JobPosting = require_attr("domain.models", "JobPosting")
    CandidateProfile = require_attr("domain.models", "CandidateProfile")
    OptimizedDocuments = require_attr("domain.models", "OptimizedDocuments")

    JobQuery(keywords=["python"], location="berlin")
    JobListing(url="https://example.com", source="test")
    JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="desc")
    CandidateProfile(summary="s", skills=["python"], experiences=[], projects=[])
    OptimizedDocuments(cv_text="cv", motivation_letter="ml", match_score=0.5, optimized_keywords=["python"])
