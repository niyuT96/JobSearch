from conftest import require_attr


def test_job_repository_save_jobs(tmp_path):
    """Method under test: storage.json_repository.JobRepository.save_jobs"""
    JobRepository = require_attr("storage.json_repository", "JobRepository")
    JobPosting = require_attr("domain.models", "JobPosting")
    repo = JobRepository()
    job = JobPosting(company_name="A", jobtitle="Dev", location="Berlin", job_description="desc")
    path = tmp_path / "jobs.json"
    repo.save_jobs([job], path)
    assert path.exists()

