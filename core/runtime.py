"""Shared runtime helpers for environment access and async execution."""

from __future__ import annotations

from typing import Awaitable, TypeVar

import asyncio
import os


T = TypeVar("T")


def get_env(name: str) -> str:
    """Return a trimmed environment variable or empty string."""

    value = os.environ.get(name)
    return value.strip() if value and value.strip() else ""


def run_async(coro: Awaitable[T]) -> T:
    """Run an async coroutine in a fresh event loop."""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        raise RuntimeError("Async execution requires a non-running event loop.")

    return asyncio.run(coro)
