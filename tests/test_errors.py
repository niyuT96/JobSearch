from conftest import require_attr


def test_pipeline_error_inheritance():
    """Methods under test: core.errors.PipelineError, core.errors.ParseError, core.errors.LLMError"""
    PipelineError = require_attr("core.errors", "PipelineError")
    ParseError = require_attr("core.errors", "ParseError")
    LLMError = require_attr("core.errors", "LLMError")
    assert issubclass(ParseError, PipelineError)
    assert issubclass(LLMError, PipelineError)

