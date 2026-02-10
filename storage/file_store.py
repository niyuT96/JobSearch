"""File storage helpers."""

from __future__ import annotations

from pathlib import Path


def write_text(path: Path, content: str) -> None:
    """Write text to disk with UTF-8 encoding.

    Args:
        path: Target file path.
        content: Text content to write.
    """

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def read_text(path: Path) -> str:
    """Read text from disk with UTF-8 encoding.

    Args:
        path: Source file path.

    Returns:
        str: File contents.
    """

    return Path(path).read_text(encoding="utf-8")
