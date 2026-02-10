from conftest import require_attr


def test_parse_job_detail_generic():
    """Method under test: parsing.job_detail_parser.parse_job_detail"""
    parse_job_detail = require_attr("parsing.job_detail_parser", "parse_job_detail")
    html = "<div id='desc'>role details</div>"
    detail = parse_job_detail(html, "generic", None, "#desc")
    assert hasattr(detail, "description")

