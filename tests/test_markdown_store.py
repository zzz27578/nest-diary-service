from app.diary.markdown_store import MarkdownDiaryStore
from app.models import DiaryEntry
from app.paths import NestPaths


def test_write_and_read_diary_entry(tmp_path):
    store = MarkdownDiaryStore(NestPaths(tmp_path))
    entry = DiaryEntry(
        date="2026-05-13",
        title="2026-05-13",
        mood=["认真", "有点烦"],
        tags=["AstrBot", "小窝"],
        people=["老爸", "小莫"],
        importance=4,
        body="## 今天发生了什么\n\n搭了小窝计划。\n\n## 我的评价\n\n这不是普通博客。",
    )

    store.write(entry)
    loaded = store.read("2026-05-13")

    assert loaded.date == "2026-05-13"
    assert loaded.mood == ["认真", "有点烦"]
    assert loaded.tags == ["AstrBot", "小窝"]
    assert "这不是普通博客" in loaded.body
