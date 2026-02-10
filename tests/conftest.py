import importlib
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def require_attr(module_name: str, attr_name: str):
    module = importlib.import_module(module_name)
    if not hasattr(module, attr_name):
        pytest.skip(f"{module_name}.{attr_name} not implemented")
    return getattr(module, attr_name)


def require_module(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        pytest.skip(f"Cannot import {module_name}: {exc}")
