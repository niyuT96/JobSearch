"""Configuration loader."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Application configuration snapshot."""

    dotenv_loaded: bool = False


def load_config() -> AppConfig:
    """Load environment variables and config files."""

    dotenv_loaded = False
    try:
        from dotenv import load_dotenv

        load_dotenv()
        dotenv_loaded = True
    except Exception:
        dotenv_loaded = False

    return AppConfig(dotenv_loaded=dotenv_loaded)
