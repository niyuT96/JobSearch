from conftest import require_attr


def test_extract_text_by_selector():
    """Method under test: parsing.html_extractors.extract_text_by_selector"""
    extract_text_by_selector = require_attr("parsing.html_extractors", "extract_text_by_selector")
    html = "<div><p id='x'>hello</p></div>"
    result = extract_text_by_selector(html, "#x")
    assert "hello" in result


def test_extract_description_by_keywords():
    """Method under test: parsing.html_extractors.extract_description_by_keywords"""
    extract_description_by_keywords = require_attr("parsing.html_extractors", "extract_description_by_keywords")
    html = "<div>python developer role</div>"
    result = extract_description_by_keywords(html, ["python"])
    assert "python" in result.lower()

