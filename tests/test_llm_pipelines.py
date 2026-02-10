from conftest import require_attr


def test_run_llm_extraction_no_jobs():
    """Method under test: pipeline.llm_extract_pipeline.run_llm_extraction"""
    run_llm_extraction = require_attr("pipeline.llm_extract_pipeline", "run_llm_extraction")
    result = run_llm_extraction([])
    assert result == []


def test_run_llm_optimization_no_jobs():
    """Method under test: pipeline.llm_optimize_pipeline.run_llm_optimization"""
    run_llm_optimization = require_attr("pipeline.llm_optimize_pipeline", "run_llm_optimization")
    CandidateProfile = require_attr("domain.models", "CandidateProfile")
    profile = CandidateProfile(summary="s", skills=["python"], experiences=[], projects=[])
    result = run_llm_optimization(profile, [])
    assert result == []

