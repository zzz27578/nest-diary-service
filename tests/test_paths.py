from app.paths import NestPaths


def test_diary_paths_are_year_month_date(tmp_path):
    paths = NestPaths(tmp_path)
    paths.ensure_all()

    assert paths.diary_file("2026-05-13") == tmp_path / "diary" / "2026" / "05" / "2026-05-13.md"
    assert (tmp_path / "media" / "blobs" / "sha256").is_dir()
    assert (tmp_path / "index").is_dir()
    assert (tmp_path / "settings").is_dir()
