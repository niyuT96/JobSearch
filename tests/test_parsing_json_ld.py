from conftest import require_attr


def test_extract_json_ld_jobposting_present():
    """Method under test: parsing.html_extractors.extract_json_ld_jobposting"""
    extract_json_ld_jobposting = require_attr("parsing.html_extractors", "extract_json_ld_jobposting")
    html = """
    <html><head>
      <script type="application/ld+json">{"@type":"JobPosting","title":"Dev"}</script>
    </head></html>
    """
    result = extract_json_ld_jobposting(html)
    assert isinstance(result, dict)
    assert result.get("@type") == "JobPosting"


def test_extract_json_ld_jobposting_missing():
    """Method under test: parsing.html_extractors.extract_json_ld_jobposting"""
    extract_json_ld_jobposting = require_attr("parsing.html_extractors", "extract_json_ld_jobposting")
    html = "<html><head></head><body>No JSON</body></html>"
    result = extract_json_ld_jobposting(html)
    assert result == {}

