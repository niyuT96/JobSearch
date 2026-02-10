"""Main application entrypoint."""

from __future__ import annotations

from app.cli import run


def main() -> int:
    """Run the CLI entrypoint and normalize the exit code.

    Returns:
        int: Exit code.
    """

    try:
        return int(run())
    except SystemExit as exc:
        try:
            return int(exc.code)
        except Exception:
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
