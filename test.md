# Test Plan (Clean Code, No Test Code)

This document lists unit tests to implement for each module based on `code structure.md`.
Each entry includes the method under test, test intent, and expected results.
No executable code is included.

## 1) app/main.py

### Method: `main()`
- Expect: Returns `0` on successful end-to-end pipeline execution.
- Expect: Returns non-zero (or raises) on unrecoverable pipeline failure.
- Expect: Logs a clear start/end message and pipeline stage boundaries.
- Expect: Uses configuration from `core/config.py` once (no duplicate loads).
- Expect: Handles empty input (no jobs found) without crashing.
- Expect: Does not perform network calls when in dry-run/test mode (if supported).

## 2) app/cli.py

### Method: `parse_args()`
- Expect: Parses keywords and location into a `JobQuery`.
- Expect: Missing required arguments yields a parser error.
- Expect: Optional flags use defaults (no implicit side effects).
- Expect: Accepts quoted keywords with spaces.

### Method: `run()`
- Expect: Passes parsed inputs to pipeline functions in correct order.
- Expect: Returns `0` on success; non-zero on failure.
- Expect: Handles exceptions by reporting user-friendly messages.
- Expect: Exits with non-zero when configuration is invalid.

## 3) core/config.py

### Method: `load_config()`
- Expect: Reads env vars and merges with defaults.
- Expect: Invalid or missing mandatory values raise a clear error.
- Expect: Output config is immutable or treated as read-only.
- Expect: Uses explicit precedence (env overrides file, or defined order).
- Expect: Ignores unknown config keys with a warning (if supported).

## 4) core/errors.py

### Class: `PipelineError`
- Expect: Can be instantiated with a message and optional cause.
- Expect: Preserves original exception as `__cause__` when provided.

### Class: `ParseError`
- Expect: Is a subclass of `PipelineError`.
- Expect: Carries parsing context (e.g., site, selector, URL).
- Expect: String representation includes site/selector/url details.

### Class: `LLMError`
- Expect: Is a subclass of `PipelineError`.
- Expect: Carries model/provider name and error details.
- Expect: String representation includes provider/model identifiers.

## 5) core/logging.py

### Method: `configure_logging(level: str | None = None)`
- Expect: Sets logging level from parameter if provided.
- Expect: Uses default level when parameter is missing.
- Expect: Installs a single handler (no duplicates on repeated calls).
- Expect: Accepts case-insensitive level names.
- Expect: Defaults to safe level when invalid level provided.

## 6) domain/models.py

### Class: `JobQuery`
- Expect: Stores keywords and location.
- Expect: Normalizes empty/whitespace keywords to empty list.
- Expect: Deduplicates keywords while preserving order (if defined).

### Class: `JobListing`
- Expect: Requires `url` and `source` fields.
- Expect: Rejects invalid URLs (or normalizes).
- Expect: Normalizes source name casing (if defined).

### Class: `JobPosting`
- Expect: Requires `company_name`, `jobtitle`, `location`, `job_description`.
- Expect: Optional fields default to empty (skills, tasks, score).
- Expect: Rejects empty `job_description` if required by pipeline.

### Class: `CandidateProfile`
- Expect: Stores summary, skills, experiences, projects.
- Expect: Validates required fields for optimization.
- Expect: Rejects empty profile when optimization requires minimum data.

### Class: `OptimizedDocuments`
- Expect: Holds CV text, motivation letter text, match score.
- Expect: Match score in [0.0, 1.0] (or defined range).
- Expect: Rejects missing CV or motivation letter text.

## 7) domain/value_objects.py

### Class: `Location`
- Expect: Normalizes casing and whitespace.
- Expect: Rejects empty strings.
- Expect: Preserves meaningful separators (e.g., "Berlin, DE").

### Class: `SkillSet`
- Expect: Deduplicates skills (case-insensitive).
- Expect: Preserves order or sorts deterministically.
- Expect: Normalizes whitespace and trims each skill.

## 8) crawling/url_generator.py

### Method: `build_search_urls(query: JobQuery) -> list[str]`
- Expect: Generates URLs for each enabled job board.
- Expect: Keywords and location are URL-encoded.
- Expect: Empty keywords or location are handled gracefully.
- Expect: Experience level is included only when provided.
- Expect: Special characters in keywords are encoded safely.
- Expect: Very long keyword lists are truncated or handled without error.

## 9) crawling/site_registry.py

### Class: `SiteConfig`
- Expect: Exposes required site fields (name, selectors, flags).
- Expect: Defaults are applied when optional fields missing.
- Expect: Missing mandatory fields raises a clear error.

### Method: `detect_site(url: str) -> SiteConfig`
- Expect: Detects known sites by URL pattern.
- Expect: Unknown site raises a clean error or returns None.
- Expect: Case-insensitive URL matching.
- Expect: Invalid URL format is handled gracefully.

## 10) crawling/playwright_client.py

### Class: `PlaywrightClient`

#### Method: `fetch(url: str, wait_for: str | None = None) -> str`
- Expect: Returns rendered HTML as string.
- Expect: Respects timeout configuration.
- Expect: Raises a predictable error on navigation failure.
- Expect: Does not allow network calls in unit tests (use mocks).
- Expect: Handles non-HTML content with a clear error or fallback.

#### Method: `fetch_iframe(url: str, selector: str) -> str`
- Expect: Follows iframe src and returns iframe HTML.
- Expect: Raises error when iframe is missing or src invalid.
- Expect: Selector matching multiple iframes uses the first (or defined rule).

## 11) parsing/html_extractors.py

### Method: `extract_json_ld_jobposting(html: str) -> dict`
- Expect: Returns JobPosting object when JSON-LD present.
- Expect: Returns empty dict when missing.
- Expect: Ignores invalid JSON-LD blocks.
- Expect: Handles multiple JSON-LD blocks and chooses the correct one.

### Method: `extract_text_by_selector(html: str, selector: str) -> str`
- Expect: Returns normalized text for first matching node.
- Expect: Raises error when selector matches nothing.
- Expect: Strips excessive whitespace and newlines.

### Method: `extract_description_by_keywords(html: str, keywords: list[str]) -> str`
- Expect: Returns best-matching block by keyword score.
- Expect: Raises error on empty keyword list.
- Expect: Handles keyword casing and partial matches consistently.

## 12) parsing/job_detail_parser.py

### Class: `JobDetail`
- Expect: Stores `description` only.
- Expect: Trims or normalizes whitespace in description.
- Expect: Rejects empty description if required by pipeline.

### Method: `parse_job_detail(html, site_type, keywords, selector) -> JobDetail`
- Expect: Uses correct extractor for each `site_type`.
- Expect: Raises error for unsupported `site_type`.
- Expect: Uses selector when provided for generic parsing.
- Expect: Uses keyword extraction when selector is not provided.

## 13) pipeline/job_ingest_pipeline.py

### Method: `ingest_jobs(query: JobQuery) -> list[JobListing]`
- Expect: Calls URL generator once.
- Expect: Returns normalized listing objects.
- Expect: Handles empty result set without error.
- Expect: Deduplicates listing URLs if generator returns duplicates.

### Method: `fetch_job_html(listing: JobListing) -> str`
- Expect: Calls crawler with listing URL.
- Expect: Returns HTML string.
- Expect: Raises or propagates crawler errors.
- Expect: Validates listing URL before fetch.

### Method: `parse_job(html: str, site: SiteConfig) -> JobPosting`
- Expect: Extracts required fields for JobPosting.
- Expect: Fails fast if required fields missing.
- Expect: Normalizes extracted text (whitespace/HTML tags).

## 14) pipeline/job_dedup.py

### Method: `deduplicate_jobs(jobs: list[JobPosting]) -> list[JobPosting]`
- Expect: Removes duplicates by (company, location, title).
- Expect: Keeps order stable (first occurrence wins).
- Expect: Does not remove distinct jobs with same company only.
- Expect: Case-insensitive comparison for company/title.

## 15) pipeline/llm_extract_pipeline.py

### Method: `run_llm_extraction(jobs: list[JobPosting]) -> list[JobPosting]`
- Expect: Calls `llm.extract_job_info.extract_job_fields` for each job.
- Expect: Preserves original jobs when LLM fails (or marks failed).
- Expect: Returns same list length as input.
- Expect: Skips LLM for jobs missing descriptions (if configured).

## 16) pipeline/llm_optimize_pipeline.py

### Method: `run_llm_optimization(profile: CandidateProfile, jobs: list[JobPosting]) -> list[OptimizedDocuments]`
- Expect: Calls `llm.optimize_documents.optimize_documents` for each job.
- Expect: Returns one output per job.
- Expect: Handles LLM failure per job without aborting all.
- Expect: Rejects empty `jobs` list with clear no-op behavior.

## 17) llm/providers.py

### Class: `LLMProvider`
- Expect: Defines a `generate(prompt: str) -> str` contract.
- Expect: Enforces error handling and retry policy (if defined).
- Expect: Rejects empty prompt with a clear error.

## 18) llm/extract_job_info.py

### Method: `extract_job_fields(job: JobPosting) -> JobPosting`
- Expect: Adds `futureTasks`, `skills`, `candidateProfile` fields.
- Expect: Leaves original description intact.
- Expect: Raises a clear error on invalid model output.
- Expect: Handles empty model response safely.

## 19) llm/optimize_documents.py

### Method: `optimize_documents(profile: CandidateProfile, job: JobPosting) -> OptimizedDocuments`
- Expect: Returns CV + motivation letter text + match score.
- Expect: Uses job context and profile inputs.
- Expect: Normalizes match score range.
- Expect: Rejects empty profile or job context as invalid input.

## 20) storage/json_repository.py

### Class: `JobRepository`

#### Method: `save_jobs(jobs: list[JobPosting], path: Path) -> None`
- Expect: Writes valid JSON with expected schema.
- Expect: Uses UTF-8 and stable ordering (if defined).
- Expect: Overwrites existing file safely or versioned output.
- Expect: Writes an empty list when `jobs` is empty.
- Expect: Rejects non-serializable fields with a clear error.

## 21) storage/file_store.py

### Method: `write_text(path: Path, content: str) -> None`
- Expect: Creates parent directory when missing (if required).
- Expect: Writes UTF-8 text without extra BOM.
- Expect: Overwrites existing file content by default.

### Method: `read_text(path: Path) -> str`
- Expect: Returns file contents as string.
- Expect: Raises error on missing file.
- Expect: Handles non-UTF8 content with a clear error or fallback.

## 22) storage/google_drive_store.py

### Class: `GoogleDriveStore`
- Expect: Upload returns file ID or URL.
- Expect: Download writes file to expected path.
- Expect: Raises clear errors on credential issues.
- Expect: Handles network timeouts with retry/backoff (if supported).

## 23) integrations/linkedin_scraper.py

### Method: `fetch_linkedin_job_urls(query: JobQuery) -> list[str]`
- Expect: Returns list of job URLs for query.
- Expect: Respects search parameters (keywords/location).
- Expect: Raises clear error if scraping is blocked or disallowed.
- Expect: Returns empty list when no results found.

## 24) tests/test_pipeline_smoke.py (integration-scope)

- Expect: End-to-end pipeline runs with mocked IO and deterministic outputs.
- Expect: No network calls in unit tests (use mocks/fakes).
- Expect: Output JSON conforms to expected schema.
- Expect: Pipeline handles zero jobs without failure.

## 25) Real URL / Input Requirements (Notes)

Some test cases require real URLs, credentials, or environment settings to be meaningful.
These should be marked as integration tests and skipped by default in unit runs.

- `crawling.playwright_client.PlaywrightClient.fetch`  
  Requires a real, reachable URL to validate rendering behavior and timeouts.
- `crawling.playwright_client.PlaywrightClient.fetch_iframe`  
  Requires a URL that contains an iframe matching the selector.
- `integrations.linkedin_scraper.fetch_linkedin_job_urls`  
  Requires real LinkedIn access; may be blocked by TOS, auth, or anti-bot defenses.
- `storage.google_drive_store.GoogleDriveStore`  
  Requires valid Google OAuth credentials and network access.
- `core.config.load_config`  
  Requires specific env vars if you test credential-dependent settings.
