from __future__ import annotations

import sqlite3

from app.models import DiaryEntry
from app.paths import NestPaths


class SearchService:
    def __init__(self, paths: NestPaths):
        self.paths = paths
        self.paths.ensure_all()
        self.db_path = self.paths.index_dir / "nest.sqlite"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS diary_meta (
                    date TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    people TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    source TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS diary_fts
                USING fts5(date UNINDEXED, title, body)
                """
            )

    def upsert_entry(self, entry: DiaryEntry) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO diary_meta
                (date, title, tags, people, mood, importance, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.date,
                    entry.normalized_title(),
                    ",".join(entry.tags),
                    ",".join(entry.people),
                    ",".join(entry.mood),
                    entry.importance,
                    entry.source,
                ),
            )
            conn.execute("DELETE FROM diary_fts WHERE date = ?", (entry.date,))
            conn.execute(
                "INSERT INTO diary_fts(date, title, body) VALUES (?, ?, ?)",
                (entry.date, entry.normalized_title(), entry.body),
            )

    def search(self, query: str, top_k: int = 8) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT date, title, snippet(diary_fts, 2, '[', ']', '...', 18)
                FROM diary_fts
                WHERE diary_fts MATCH ?
                LIMIT ?
                """,
                (query, top_k),
            ).fetchall()
        return [{"date": row[0], "title": row[1], "snippet": row[2]} for row in rows]
