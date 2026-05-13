from app.models import DiaryEntry
from app.paths import NestPaths
from app.search.search_service import SearchService


def test_search_returns_relevant_entries(tmp_path):
    service = SearchService(NestPaths(tmp_path))
    service.upsert_entry(
        DiaryEntry(
            date="2026-05-13",
            title="小窝计划",
            tags=["AstrBot"],
            people=["老爸"],
            body="今天决定做 bot 私密小窝，不做公开博客。",
        )
    )

    results = service.search("私密", top_k=5)

    assert len(results) == 1
    assert results[0]["date"] == "2026-05-13"
    assert "私密" in results[0]["snippet"]
