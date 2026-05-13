from __future__ import annotations

from app.diary.markdown_store import MarkdownDiaryStore
from app.diary.revision_service import RevisionService
from app.models import DiaryEntry
from app.paths import NestPaths
from app.search.search_service import SearchService


class DiaryService:
    def __init__(self, paths: NestPaths):
        self.paths = paths
        self.store = MarkdownDiaryStore(paths)
        self.search_service = SearchService(paths)
        self.revisions = RevisionService(paths)

    def write_diary(self, entry: DiaryEntry, reason: str = "") -> DiaryEntry:
        diary_path = self.paths.diary_file(entry.date)
        if diary_path.exists():
            self.revisions.snapshot(
                date=entry.date,
                content=diary_path.read_text(encoding="utf-8"),
                reason=reason or "overwrite diary entry",
                source="write_diary",
            )
        self.store.write(entry)
        self.search_service.upsert_entry(entry)
        return entry

    def read_by_date(self, date: str) -> DiaryEntry:
        return self.store.read(date)

    def search(self, query: str, top_k: int = 8) -> list[dict]:
        return self.search_service.search(query=query, top_k=top_k)

    def list_entries(self) -> list[DiaryEntry]:
        return self.store.list_entries()
