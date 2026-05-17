from app.diary.diary_service import DiaryService
from app.media.media_service import MediaService
from app.models import DiaryEntry
from app.paths import NestPaths


def test_overwrite_creates_revision(tmp_path):
    service = DiaryService(NestPaths(tmp_path))
    service.write_diary(DiaryEntry(date="2026-05-13", body="old"))
    service.write_diary(DiaryEntry(date="2026-05-13", body="new"), reason="test overwrite")

    revisions = list((tmp_path / "revisions" / "diary" / "2026" / "05" / "2026-05-13").glob("*.md"))
    assert len(revisions) == 1
    assert "old" in revisions[0].read_text(encoding="utf-8")


def test_delete_creates_revision_and_removes_diary(tmp_path):
    service = DiaryService(NestPaths(tmp_path))
    service.write_diary(DiaryEntry(date="2026-05-13", title="旧日记", body="old"))

    assert service.delete_diary("2026-05-13", reason="test delete")

    assert not (tmp_path / "diary" / "2026" / "05" / "2026-05-13.md").exists()
    revisions = list((tmp_path / "revisions" / "diary" / "2026" / "05" / "2026-05-13").glob("*.md"))
    assert len(revisions) == 1
    assert "old" in revisions[0].read_text(encoding="utf-8")
    assert service.search("old", top_k=5) == []


def test_media_is_content_addressed(tmp_path):
    media = MediaService(NestPaths(tmp_path))
    source = tmp_path / "input.png"
    source.write_bytes(b"same image")

    record = media.save_media(source, date="2026-05-13")

    assert record["sha256"]
    assert (tmp_path / "media" / "by-date" / "2026" / "05" / "2026-05-13" / "manifest.json").exists()
