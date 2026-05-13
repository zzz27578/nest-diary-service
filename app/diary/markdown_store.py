from __future__ import annotations

import json
from pathlib import Path

from app.models import DiaryEntry
from app.paths import NestPaths


class MarkdownDiaryStore:
    def __init__(self, paths: NestPaths):
        self.paths = paths
        self.paths.ensure_all()

    def write(self, entry: DiaryEntry) -> Path:
        path = self.paths.diary_file(entry.date)
        path.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = {
            "date": entry.date,
            "title": entry.normalized_title(),
            "mood": entry.mood,
            "tags": entry.tags,
            "people": entry.people,
            "importance": entry.importance,
            "source": entry.source,
            "revision": entry.revision,
        }
        lines = ["---"]
        for key, value in frontmatter.items():
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        lines.extend(["---", "", f"# {entry.normalized_title()}", "", entry.body.rstrip(), ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def read(self, date: str) -> DiaryEntry:
        path = self.paths.diary_file(date)
        text = path.read_text(encoding="utf-8")
        _prefix, meta_text, body_text = text.split("---", 2)
        meta = {}
        for line in meta_text.strip().splitlines():
            key, raw_value = line.split(":", 1)
            meta[key.strip()] = json.loads(raw_value.strip())

        body_lines = body_text.strip().splitlines()
        if body_lines and body_lines[0].startswith("# "):
            body_lines = body_lines[1:]
        body = "\n".join(body_lines).strip()
        return DiaryEntry(
            date=meta["date"],
            title=meta.get("title"),
            mood=meta.get("mood", []),
            tags=meta.get("tags", []),
            people=meta.get("people", []),
            importance=meta.get("importance", 3),
            source=meta.get("source", "bot"),
            revision=meta.get("revision", 1),
            body=body,
        )

    def list_entries(self) -> list[DiaryEntry]:
        entries: list[DiaryEntry] = []
        for path in sorted(self.paths.diary_dir.glob("*/*/*.md"), reverse=True):
            try:
                entries.append(self.read(path.stem))
            except Exception:
                continue
        return entries
