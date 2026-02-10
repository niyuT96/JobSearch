# AI-Powered Job Search System - Code Structure

This document proposes a clean, readable project structure based on `ProjectPlan.drawio.png`
and the current repository files. It follows Clean Code principles: clear naming, single
responsibility, small modules, explicit data flow, and testable units.

## 1) High-Level Architecture

Pipeline stages (from the diagram):

1. **Search Input**: keywords, location.
2. **URL Generation**: job boards + site-specific filters.
3. **Crawling**: Playwright fetches rendered HTML.
4. **Parsing**: extract job description and metadata.
5. **De-duplication** *(optional)*: merge same jobs across platforms.
6. **Lightweight LLM**: extract structured fields + skills + tasks.
7. **Advanced LLM**: optimize CV and motivation letter using job context.
8. **Output**: JSON results, optimized keywords, score, and documents.

## 2) Proposed Project Tree (Clean Code)

```
JobSearch/
  README.md
  code structure.md
  SystemPrompt.md
  ProjectPlan.drawio.png

  app/
    __init__.py
    main.py
    cli.py

  core/
    __init__.py
    config.py
    errors.py
    logging.py

  domain/
    __init__.py
    models.py
    value_objects.py

  crawling/
    __init__.py
    playwright_client.py
    site_registry.py
    url_generator.py

  parsing/
    __init__.py
    job_detail_parser.py
    html_extractors.py

  pipeline/
    __init__.py
    job_ingest_pipeline.py
    job_dedup.py
    llm_extract_pipeline.py
    llm_optimize_pipeline.py

  llm/
    __init__.py
    prompts/
      system_prompt.md
      user_prompt.md
    providers.py
    extract_job_info.py
    optimize_documents.py

  storage/
    __init__.py
    json_repository.py
    file_store.py
    google_drive_store.py

  integrations/
    __init__.py
    linkedin_scraper.py

  tests/
    test_url_generator.py
    test_parsing_json_ld.py
    test_dedup.py
    test_llm_extract.py
    test_pipeline_smoke.py
```

Notes:
- `app/` contains entrypoints (CLI, orchestration).
- `core/` contains shared configuration, errors, logging.
- `domain/` contains data models and core business concepts.
- `crawling/` isolates Playwright behavior and site settings.
- `parsing/` isolates HTML parsing and site-specific extraction.
- `pipeline/` orchestrates the end-to-end flow in small steps.
- `llm/` contains prompts and model calls for extraction and optimization.
- `storage/` handles persistence (JSON and optional Google Drive).
- `integrations/` holds external tools such as LinkedIn-specific scrapers.

## 3) Current Files Mapped to Structure

- `playwright_fetch_html.py` -> `crawling/playwright_client.py`
- `job_detail_parser.py` -> `parsing/job_detail_parser.py`
- `getJobInfo.py` -> `app/cli.py` or `pipeline/job_ingest_pipeline.py`

## 4) Domain Models (Clean, Explicit Types)

### `domain/models.py`

Classes:
- `JobQuery`
  - Purpose: Encapsulates search parameters (keywords, location).
- `JobListing`
  - Purpose: Represents a single job listing with URL and source site.
- `JobPosting`
  - Purpose: Structured job details after parsing and LLM extraction.
- `CandidateProfile`
  - Purpose: User profile data used for optimization.
- `OptimizedDocuments`
  - Purpose: Output of LLM optimization (CV + motivation letter + score).

### `domain/value_objects.py`

Classes:
- `Location`
  - Purpose: normalized location string or geo identifier.
- `SkillSet`
  - Purpose: normalized list of skills with optional weights.

## 5) Modules and Their Responsibilities

### `app/main.py`
- Function: `main()`
  - Type: **orchestration**
  - Description: Main entrypoint to run the full pipeline.

### `app/cli.py`
- Function: `parse_args()`
  - Type: **input parsing**
  - Description: Parse CLI args into `JobQuery` and options.
- Function: `run()`
  - Type: **orchestration**
  - Description: Pass CLI inputs into the pipeline and handle output.

### `core/config.py`
- Function: `load_config()`
  - Type: **configuration**
  - Description: Load env vars and config files into a config object.

### `core/errors.py`
- Class: `PipelineError`
  - Purpose: Base error for pipeline failures.
- Class: `ParseError`
  - Purpose: Parsing failure with context.
- Class: `LLMError`
  - Purpose: LLM call failure or malformed response.

### `crawling/url_generator.py`
- Function: `build_search_urls(query: JobQuery) -> list[str]`
  - Type: **business logic**
  - Description: Build job board URLs from query parameters.

### `crawling/site_registry.py`
- Class: `SiteConfig`
  - Purpose: Central configuration of per-site behavior.
- Function: `detect_site(url: str) -> SiteConfig`
  - Type: **lookup**
  - Description: Identify site configuration by URL.

### `crawling/playwright_client.py`
- Class: `PlaywrightClient`
  - Purpose: Encapsulate Playwright usage to fetch rendered HTML.
- Method: `fetch(url: str, wait_for: str | None) -> str`
  - Type: **IO**
  - Description: Return rendered HTML for a URL.
- Method: `fetch_iframe(url: str, selector: str) -> str`
  - Type: **IO**
  - Description: Follow iframe source when required.

### `parsing/html_extractors.py`
- Function: `extract_json_ld_jobposting(html: str) -> dict`
  - Type: **parsing**
  - Description: Find JobPosting in JSON-LD schema.
- Function: `extract_text_by_selector(html: str, selector: str) -> str`
  - Type: **parsing**
  - Description: Extract text by CSS selector.
- Function: `extract_description_by_keywords(html: str, keywords: list[str]) -> str`
  - Type: **parsing**
  - Description: Best-effort description by keyword scoring.

### `parsing/job_detail_parser.py`
- Function: `parse_job_detail(...) -> JobDetail`
  - Type: **parsing**
  - Description: Dispatch extraction based on site type.
- Class: `JobDetail`
  - Purpose: Minimal parsed output (raw description).

### `pipeline/job_ingest_pipeline.py`
- Function: `ingest_jobs(query: JobQuery) -> list[JobListing]`
  - Type: **orchestration**
  - Description: Generate URLs and retrieve job listing links.
- Function: `fetch_job_html(listing: JobListing) -> str`
  - Type: **IO**
  - Description: Fetch HTML via crawler.
- Function: `parse_job(html: str, site: SiteConfig) -> JobPosting`
  - Type: **parsing**
  - Description: Convert HTML to structured `JobPosting`.

### `pipeline/job_dedup.py`
- Function: `deduplicate_jobs(jobs: list[JobPosting]) -> list[JobPosting]`
  - Type: **business logic**
  - Description: Remove same jobs by (company, location, title).

### `llm/extract_job_info.py`
- Function: `extract_job_fields(job: JobPosting) -> JobPosting`
  - Type: **LLM extraction**
  - Description: Use lightweight LLM to add tasks, skills, profile fit.

### `llm/optimize_documents.py`
- Function: `optimize_documents(profile: CandidateProfile, job: JobPosting) -> OptimizedDocuments`
  - Type: **LLM optimization**
  - Description: Use advanced LLM to optimize CV and motivation letter.

### `storage/json_repository.py`
- Class: `JobRepository`
  - Purpose: Save and load jobs as JSON.
- Method: `save_jobs(jobs: list[JobPosting], path: Path) -> None`
  - Type: **IO**
  - Description: Persist data to JSON.

### `storage/google_drive_store.py`
- Class: `GoogleDriveStore`
  - Purpose: Optional upload/download to Google Drive.

## 6) Current Code (File-Level Description)

### `getJobInfo.py`
Purpose: CLI utility to fetch a single job URL, render HTML, and extract job info.

Functions:
- `parse_args()`  
  - Type: **input parsing**
  - Description: CLI argument parsing for a single URL.
- `detect_site(url)`  
  - Type: **lookup**
  - Description: Delegates to `playwright_fetch_html.detect_site_from_url`.
- `resolve_output(site, override)`  
  - Type: **configuration**
  - Description: Determine output file path for rendered HTML.
- `fetch_html(url, site)`  
  - Type: **IO**
  - Description: Fetch rendered HTML, optionally follow iframe.
- `parse_result(html, site)`  
  - Type: **parsing**
  - Description: Parse content based on site rules.
- `main()`  
  - Type: **orchestration**
  - Description: End-to-end job fetch and parse for one URL.

### `job_detail_parser.py`
Purpose: Extract job description from saved HTML using site presets or generic logic.

Class:
- `JobDetail`  
  - Description: Holds extracted job description.

Functions:
- `parse_args()`  
  - Type: **input parsing**
  - Description: CLI argument parsing for parsing HTML.
- `parse_job_detail(html, site_type, keywords, selector)`  
  - Type: **parsing**
  - Description: Dispatch to site-specific extraction.
- `extract_description_linkedin(html)`  
  - Type: **parsing**
  - Description: Extract LinkedIn job description from JSON payload.
- `extract_description_json_ld(html)`  
  - Type: **parsing**
  - Description: Extract description from JSON-LD JobPosting.
- `extract_jobposting_json_ld(html)`  
  - Type: **parsing**
  - Description: Locate JobPosting JSON-LD block.
- `extract_description_by_keywords(html, keywords)`  
  - Type: **parsing**
  - Description: Best match block by keyword scoring.
- `extract_text_by_selector(html, selector)`  
  - Type: **parsing**
  - Description: Extract text from CSS selector.
- `main()`  
  - Type: **orchestration**
  - Description: CLI flow for saved HTML parsing.

### `playwright_fetch_html.py`
Purpose: Fetch fully-rendered HTML using Playwright.

Functions:
- `parse_args()`  
  - Type: **input parsing**
  - Description: CLI arguments for HTML fetching.
- `fetch_rendered_html(url, wait_for, timeout_ms, headless, wait_jobposting)`  
  - Type: **IO**
  - Description: Render a page and return HTML.
- `extract_iframe_src(html, selector, base_url)`  
  - Type: **parsing**
  - Description: Find iframe source from HTML.
- `apply_site_preset(args)`  
  - Type: **configuration**
  - Description: Apply per-site fetch settings.
- `detect_site_from_url(url)`  
  - Type: **lookup**
  - Description: Detect site type by URL.
- `default_output_for_site(site)`  
  - Type: **configuration**
  - Description: Output file name per site.
- `main()`  
  - Type: **orchestration**
  - Description: CLI execution of Playwright fetch.

## 7) Data Contracts (JSON)

Suggested minimal contract for a job:

```
{
  "id": "string",
  "url": "string",
  "company_name": "string",
  "jobtitle": "string",
  "location": "string",
  "job_description": "string",
  "futureTasks": ["string"],
  "candidateProfile": "string",
  "skills": ["string"],
  "matchScore": 0.0,
  "optimizedKeywords": ["string"]
}
```

## 8) Clean Code Guidelines Applied

- **Small functions**: each function does one thing.
- **Explicit types**: use dataclasses for domain models.
- **No hidden I/O**: keep network/file operations in IO layers.
- **Pure parsing**: HTML parsing functions should be deterministic.
- **Consistent naming**: verbs for functions, nouns for classes.
- **Single responsibility**: avoid mixing crawling, parsing, and LLM logic.
- **Testability**: LLM logic isolated behind a provider interface.

## 9) Future Extensions

- Add `linkedin_scraper.py` only if allowed by LinkedIn terms.
- Add cache layer for HTML and parsed results.
- Add async Playwright for batch crawling.
- Add evaluation harness for LLM extraction quality.
