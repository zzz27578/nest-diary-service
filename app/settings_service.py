from __future__ import annotations

import json
import secrets
from dataclasses import asdict

from app.models import SecuritySettings, ServiceUiSettings
from app.paths import NestPaths


class ServiceSettingsStore:
    def __init__(self, paths: NestPaths):
        self.paths = paths
        self.paths.ensure_all()
        self.path = self.paths.settings_dir / "service-ui.json"

    def load(self) -> ServiceUiSettings:
        if not self.path.exists():
            return ServiceUiSettings()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        defaults = asdict(ServiceUiSettings())
        defaults.update(data)
        return ServiceUiSettings(**defaults)

    def save(self, settings: ServiceUiSettings) -> ServiceUiSettings:
        settings.search_default_top_k = max(1, min(int(settings.search_default_top_k), 50))
        if settings.diary_archive_granularity not in {"day", "month", "year"}:
            settings.diary_archive_granularity = "day"
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return settings


class SecuritySettingsStore:
    def __init__(self, paths: NestPaths, default_admin_password: str = "12345678", default_bot_api_token: str = ""):
        self.paths = paths
        self.paths.ensure_all()
        self.path = self.paths.settings_dir / "security.json"
        self.default_admin_password = default_admin_password or "12345678"
        self.default_bot_api_token = default_bot_api_token

    def load(self) -> SecuritySettings:
        defaults = {
            "admin_password": self.default_admin_password,
            "bot_api_token": self.default_bot_api_token,
        }
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            defaults.update(data)
        return SecuritySettings(**defaults)

    def save(self, settings: SecuritySettings) -> SecuritySettings:
        settings.admin_password = settings.admin_password or self.default_admin_password
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return settings

    def update(self, admin_password: str | None = None, bot_api_token: str | None = None) -> SecuritySettings:
        current = self.load()
        if admin_password:
            current.admin_password = admin_password
        if bot_api_token is not None:
            current.bot_api_token = bot_api_token
        return self.save(current)

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)
