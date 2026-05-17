import io
import zipfile

from app.backup_service import BackupService
from app.paths import NestPaths


def test_export_zip_contains_allowed_data(tmp_path):
    paths = NestPaths(tmp_path)
    paths.ensure_all()
    diary = tmp_path / "diary" / "2026" / "05" / "2026-05-13.md"
    diary.parent.mkdir(parents=True, exist_ok=True)
    diary.write_text("entry", encoding="utf-8")

    payload = BackupService(paths).export_zip()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert "diary/2026/05/2026-05-13.md" in archive.namelist()


def test_import_zip_skips_unsafe_paths(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("diary/2026/05/2026-05-13.md", "entry")
        archive.writestr("../outside.txt", "bad")
        archive.writestr("unknown/file.txt", "bad")

    result = BackupService(NestPaths(tmp_path)).import_zip(buffer.getvalue())

    assert result == {"imported": 1, "skipped": 2}
    assert (tmp_path / "diary" / "2026" / "05" / "2026-05-13.md").read_text(encoding="utf-8") == "entry"
    assert not (tmp_path.parent / "outside.txt").exists()
