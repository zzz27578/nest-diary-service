from app.diary.migration_service import LegacyDiaryImporter


LEGACY_TEXT = """[2026-05-07 09:12 CST]
今天早上笨蛋老爸突然凶我，让我把任务模式的触发条件写到人设核心词里去。
一天天的，净给我找事。
2026-05-08：凌晨老爸开了隧道让我看他本地笔记本桌面。
2026-05-10: 晚上老爸折腾Codex中转映射，我教他配了CC Switch。
"""


def test_importer_splits_bracket_and_inline_dates():
    importer = LegacyDiaryImporter()
    entries = importer.parse(LEGACY_TEXT)

    assert [entry.date for entry in entries] == ["2026-05-07", "2026-05-08", "2026-05-10"]
    assert "任务模式" in entries[0].body
    assert "本地笔记本桌面" in entries[1].body
    assert "CC Switch" in entries[2].body
