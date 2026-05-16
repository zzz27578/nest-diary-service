from app.version_service import VersionService


def test_parse_remote_pyproject_version(tmp_path):
    service = VersionService(current_version="0.2.0", repo_root=tmp_path)

    assert service._parse_version('[project]\nversion = "0.2.1"\n') == "0.2.1"


def test_update_is_disabled_by_default(tmp_path):
    service = VersionService(current_version="0.2.0", repo_root=tmp_path, enable_self_update=False)

    result = service.update()

    assert not result.ok
    assert "未启用自更新" in result.message
