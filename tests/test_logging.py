from conftest import require_attr


def test_configure_logging_idempotent():
    """Method under test: core.logging.configure_logging"""
    configure_logging = require_attr("core.logging", "configure_logging")
    configure_logging()
    configure_logging()
    assert True

