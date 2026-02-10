"""Domain value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Location:
    """Normalized location string."""

    value: str

    def __post_init__(self) -> None:
        cleaned = (self.value or "").strip()
        if not cleaned:
            raise ValueError("Location cannot be empty.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SkillSet:
    """Normalized list of skills with optional weights."""

    skills: List[str]

    def __post_init__(self) -> None:
        normalized: List[str] = []
        seen = set()
        for skill in (self.skills or []):
            cleaned = (skill or "").strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(cleaned)
        object.__setattr__(self, "skills", normalized)

    def __iter__(self):
        return iter(self.skills)

    def __len__(self) -> int:
        return len(self.skills)

    def __contains__(self, item: str) -> bool:
        return item in self.skills

    @classmethod
    def from_iterable(cls, values: Iterable[str]) -> "SkillSet":
        return cls(list(values))
