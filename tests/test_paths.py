from app.paths import NestPaths


def test_diary_paths_are_year_month_date(tmp_path):
    paths = NestPaths(tmp_path)
    paths.ensure_all()

    assert paths.diary_file("2026-05-13") == (
        tmp_path / "modules" / "diary" / "entries" / "2026" / "05" / "2026-05-13.md"
    )
    assert (tmp_path / "modules" / "media" / "blobs" / "sha256").is_dir()
    assert (tmp_path / "modules" / "diary" / "index").is_dir()
    assert (tmp_path / "system" / "settings").is_dir()
    assert (tmp_path / "user_custom" / "webui" / "themes").is_dir()


def test_legacy_layout_is_copied_into_modules(tmp_path):
    legacy = tmp_path / "diary" / "2026" / "05" / "2026-05-13.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("legacy diary", encoding="utf-8")

    paths = NestPaths(tmp_path)
    paths.ensure_all()

    migrated = tmp_path / "modules" / "diary" / "entries" / "2026" / "05" / "2026-05-13.md"
    assert migrated.read_text(encoding="utf-8") == "legacy diary"
    assert legacy.exists()
