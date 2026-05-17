from app.models import ServiceUiSettings
from app.paths import NestPaths
from app.settings_service import SecuritySettingsStore, ServiceSettingsStore


def test_service_settings_roundtrip(tmp_path):
    store = ServiceSettingsStore(NestPaths(tmp_path))
    store.save(
        ServiceUiSettings(
            search_default_top_k=9,
            enable_diary_module=False,
            diary_archive_granularity="month",
            allow_media_refs=False,
            show_impression_prompt=False,
            active_frontend_style="custom",
            custom_webui_dir="user_custom/webui",
            backup_custom_before_update=False,
            impression_prompt="custom prompt",
        )
    )

    loaded = store.load()

    assert loaded.search_default_top_k == 9
    assert not loaded.enable_diary_module
    assert loaded.diary_archive_granularity == "month"
    assert not loaded.allow_media_refs
    assert loaded.active_frontend_style == "custom"
    assert loaded.custom_webui_dir == "user_custom/webui"
    assert not loaded.backup_custom_before_update
    assert loaded.impression_prompt == "custom prompt"


def test_security_settings_default_and_update(tmp_path):
    store = SecuritySettingsStore(NestPaths(tmp_path))

    assert store.load().admin_password == "12345678"

    updated = store.update(admin_password="new-password", bot_api_token="token-1", external_api_enabled=True)

    assert updated.admin_password == "new-password"
    assert store.load().bot_api_token == "token-1"
    assert store.load().external_api_enabled
