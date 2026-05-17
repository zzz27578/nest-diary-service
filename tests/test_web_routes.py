import io
import zipfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backup_service import BackupService
from app.diary.diary_service import DiaryService
from app.memory.impression_service import ImpressionService
from app.paths import NestPaths
from app.settings_service import SecuritySettingsStore, ServiceSettingsStore
from app.web.routes import create_web_router
from app.web_auth import WebSessionAuth


def _client(tmp_path):
    paths = NestPaths(tmp_path)
    diary = DiaryService(paths)
    auth = WebSessionAuth(admin_password="12345678", session_secret="test-secret")
    app = FastAPI()
    app.include_router(
        create_web_router(
            auth,
            diary,
            None,
            diary.revisions,
            ImpressionService(paths),
            ServiceSettingsStore(paths),
            SecuritySettingsStore(paths),
            auth,
            None,
            BackupService(paths),
            None,
        )
    )
    client = TestClient(app)
    client.post("/login", data={"password": "12345678"})
    return client


def test_web_can_write_edit_delete_and_export(tmp_path):
    client = _client(tmp_path)

    response = client.post(
        "/write/diary",
        data={
            "date": "2026-05-17",
            "title": "测试标题",
            "body": "测试正文",
            "mood": "calm",
            "tags": "test",
            "people": "admin",
            "importance": "3",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "测试标题" in client.get("/diary?date=2026-05-17").text

    export = client.get("/settings/export")
    assert export.status_code == 200
    assert export.headers["content-type"] == "application/zip"

    response = client.post("/diary/delete", data={"date": "2026-05-17"}, follow_redirects=False)
    assert response.status_code == 303
    assert "测试标题" not in client.get("/diary").text


def test_web_import_rebuilds_diary_index(tmp_path):
    client = _client(tmp_path)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "diary/2026/05/2026-05-17.md",
            '---\ndate: "2026-05-17"\ntitle: "导入标题"\nmood: []\ntags: ["import"]\npeople: []\nmedia_refs: []\nimportance: 3\nsource: "bot"\nrevision: 1\n---\n\n# 导入标题\n\n导入正文\n',
        )

    response = client.post(
        "/settings/import",
        files={"backup_file": ("backup.zip", buffer.getvalue(), "application/zip")},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "导入标题" in client.get("/search?q=导入").text
