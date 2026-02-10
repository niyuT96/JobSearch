from conftest import require_attr


def test_load_config_returns_object():
    """Method under test: core.config.load_config"""
    load_config = require_attr("core.config", "load_config")
    config = load_config()
    assert config is not None

