import pytest

from conftest import require_attr


def test_cli_parse_args_missing_required(monkeypatch):
    """Method under test: app.cli.parse_args"""
    parse_args = require_attr("app.cli", "parse_args")
    monkeypatch.setattr("sys.argv", ["cli.py"]) 
    try:
        parse_args()
    except SystemExit:
        assert True
    else:
        assert False


def test_cli_run_returns_int(monkeypatch):
    """Method under test: app.cli.run"""
    run = require_attr("app.cli", "run")
    try:
        result = run()
    except SystemExit:
        return
    assert isinstance(result, int)

