from conftest import require_attr


def test_pipeline_smoke_with_real_flow():
    """Methods under test: pipeline.job_ingest_pipeline.ingest_jobs,
    pipeline.llm_extract_pipeline.run_llm_extraction,
    pipeline.llm_optimize_pipeline.run_llm_optimization.
    """
    ingest_jobs = require_attr("pipeline.job_ingest_pipeline", "ingest_jobs")
    parse_job = require_attr("pipeline.job_ingest_pipeline", "parse_job")
    run_llm_extraction = require_attr("pipeline.llm_extract_pipeline", "run_llm_extraction")
    run_llm_optimization = require_attr("pipeline.llm_optimize_pipeline", "run_llm_optimization")

    JobQuery = require_attr("domain.models", "JobQuery")
    CandidateProfile = require_attr("domain.models", "CandidateProfile")
    JobPosting = require_attr("domain.models", "JobPosting")

    query = JobQuery(keywords=["python"], location="berlin")
    profile = CandidateProfile(summary="s", skills=["python"], experiences=[], projects=[])

    listings = ingest_jobs(query)
    html_fixture = "<div>job description placeholder</div>"
    postings = [parse_job(html_fixture, None) for _ in listings]

    enriched = run_llm_extraction(postings)
    docs = run_llm_optimization(profile, enriched)
    assert isinstance(docs, list)
