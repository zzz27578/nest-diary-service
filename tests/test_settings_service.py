from app.models import ServiceUiSettings
from app.paths import NestPaths
from app.settings_service import ServiceSettingsStore


def test_service_settings_roundtrip(tmp_path):
    store = ServiceSettingsStore(NestPaths(tmp_path))
    store.save(
        ServiceUiSettings(
            search_default_top_k=9,
            diary_archive_granularity="month",
            allow_media_refs=False,
            show_impression_prompt=False,
            impression_prompt="custom prompt",
        )
    )

    loaded = store.load()

    assert loaded.search_default_top_k == 9
    assert loaded.diary_archive_granularity == "month"
    assert not loaded.allow_media_refs
    assert loaded.impression_prompt == "custom prompt"
