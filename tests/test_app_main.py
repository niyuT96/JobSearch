from conftest import require_attr


def test_main_returns_int():
    """Method under test: app.main.main"""
    main = require_attr("app.main", "main")
    result = main()
    assert isinstance(result, int)

