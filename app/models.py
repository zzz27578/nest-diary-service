from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DiaryEntry:
    date: str
    body: str
    title: str | None = None
    mood: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    importance: int = 3
    source: str = "bot"
    revision: int = 1

    def normalized_title(self) -> str:
        return self.title or self.date
