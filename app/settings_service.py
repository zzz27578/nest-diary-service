from __future__ import annotations

import json
from dataclasses import asdict

from app.models import ServiceUiSettings
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
