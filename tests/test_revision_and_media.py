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


def test_media_is_content_addressed(tmp_path):
    media = MediaService(NestPaths(tmp_path))
    source = tmp_path / "input.png"
    source.write_bytes(b"same image")

    record = media.save_media(source, date="2026-05-13")

    assert record["sha256"]
    assert (tmp_path / "media" / "by-date" / "2026" / "05" / "2026-05-13" / "manifest.json").exists()
