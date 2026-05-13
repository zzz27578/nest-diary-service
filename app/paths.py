from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NestPaths:
    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root))

    @property
    def diary_dir(self) -> Path:
        return self.root / "diary"

    @property
    def index_dir(self) -> Path:
        return self.root / "index"

    def diary_file(self, date: str) -> Path:
        year, month, _day = date.split("-")
        return self.diary_dir / year / month / f"{date}.md"

    def ensure_all(self) -> None:
        for path in [
            self.diary_dir,
            self.root / "memory" / "people",
            self.root / "memory" / "topics",
            self.root / "memory" / "events",
            self.root / "archive" / "monthly",
            self.root / "archive" / "yearly",
            self.root / "media" / "blobs" / "sha256",
            self.root / "media" / "variants",
            self.root / "media" / "by-date",
            self.root / "drafts",
            self.root / "revisions",
            self.root / "imports",
            self.root / "logs",
            self.index_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)
