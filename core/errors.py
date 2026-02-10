"""Custom error types used across the pipeline."""


class PipelineError(Exception):
    """Base error for pipeline failures."""


class ParseError(PipelineError):
    """Parsing failure with context."""


class LLMError(PipelineError):
    """LLM call failure or malformed response."""
