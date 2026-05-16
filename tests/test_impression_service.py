from app.memory.impression_service import ImpressionService
from app.models import PersonImpression
from app.paths import NestPaths


def test_write_and_read_person_impression(tmp_path):
    service = ImpressionService(NestPaths(tmp_path))
    item = PersonImpression(
        name="admin",
        summary="Prefers direct local previews and clear implementation details.",
        traits=["direct", "detail-oriented"],
        interests=["AI", "AstrBot"],
        preferences=["local preview", "clear docs"],
        relationship="project owner",
        evidence_dates=["2026-05-13", "2026-05-16"],
        confidence=4,
        notes="Keep evidence dates traceable.",
    )

    service.save(item)
    loaded = service.get("admin")

    assert loaded is not None
    assert loaded.name == "admin"
    assert loaded.confidence == 4
    assert "local preview" in loaded.preferences
    assert loaded.updated_at


def test_impression_confidence_is_clamped(tmp_path):
    service = ImpressionService(NestPaths(tmp_path))
    service.save(PersonImpression(name="person", summary="summary", confidence=9))

    loaded = service.get("person")

    assert loaded is not None
    assert loaded.confidence == 5
