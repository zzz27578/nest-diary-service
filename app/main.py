from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .auth import verify_bearer_token
from .config import load_settings
from .diary.diary_service import DiaryService
from .memory.impression_service import ImpressionService
from .media.media_service import MediaService
from .models import DiaryEntry, PersonImpression
from .paths import NestPaths
from .web.routes import create_web_router, mount_static
from .web_auth import WebSessionAuth

settings = load_settings()
app = FastAPI(title="Nest Diary Service", version="0.1.0")
paths = NestPaths(settings.data_dir)
diary_service = DiaryService(paths)
media_service = MediaService(paths)
impression_service = ImpressionService(paths)
web_auth = WebSessionAuth(
    admin_password=settings.admin_password,
    session_secret=settings.bot_api_token or "development-session-secret",
)
mount_static(app)
app.include_router(
    create_web_router(
        web_auth,
        diary_service,
        media_service,
        diary_service.revisions,
        impression_service,
    )
)


class DiaryWriteRequest(BaseModel):
    date: str
    body: str
    title: str | None = None
    mood: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    importance: int = 3
    source: str = "bot"
    reason: str = ""
    intent: str = "write_diary"
    idempotency_key: str | None = None


def require_bot_token(authorization: str | None = Header(default=None)) -> None:
    verify_bearer_token(settings.bot_api_token, authorization)


@app.get("/api/v1/status")
async def status(_auth: None = Depends(require_bot_token)):
    return {
        "status": "ok",
        "service": "nest-diary",
        "data_dir": str(settings.data_dir),
    }


@app.post("/api/v1/diary/write")
async def write_diary(payload: DiaryWriteRequest, _auth: None = Depends(require_bot_token)):
    entry = DiaryEntry(
        date=payload.date,
        title=payload.title,
        body=payload.body,
        mood=payload.mood,
        tags=payload.tags,
        people=payload.people,
        importance=payload.importance,
        source=payload.source,
    )
    saved = diary_service.write_diary(entry, reason=payload.reason)
    return {"status": "ok", "date": saved.date, "title": saved.normalized_title()}


@app.get("/api/v1/diary/search")
async def search_diary(q: str, top_k: int = 8, _auth: None = Depends(require_bot_token)):
    return {"query": q, "results": diary_service.search(q, top_k=top_k)}


@app.get("/api/v1/diary/{date}")
async def read_diary(date: str, _auth: None = Depends(require_bot_token)):
    try:
        entry = diary_service.read_by_date(date)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Diary entry not found") from None
    return {
        "date": entry.date,
        "title": entry.normalized_title(),
        "mood": entry.mood,
        "tags": entry.tags,
        "people": entry.people,
        "importance": entry.importance,
        "source": entry.source,
        "revision": entry.revision,
        "body": entry.body,
    }


class MediaAttachRequest(BaseModel):
    source_path: str
    date: str
    original_name: str | None = None


@app.post("/api/v1/media/attach")
async def attach_media(payload: MediaAttachRequest, _auth: None = Depends(require_bot_token)):
    source = Path(payload.source_path)
    if not source.exists():
        raise HTTPException(status_code=404, detail="Media source file not found")
    record = media_service.save_media(source, date=payload.date, original_name=payload.original_name)
    return {"status": "ok", "asset": record}


class ImpressionWriteRequest(BaseModel):
    name: str
    summary: str
    traits: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    relationship: str = ""
    evidence_dates: list[str] = Field(default_factory=list)
    confidence: int = 3
    notes: str = ""


@app.get("/api/v1/impressions")
async def list_impressions(_auth: None = Depends(require_bot_token)):
    return {"items": [item.__dict__ for item in impression_service.list_people()]}


@app.get("/api/v1/impressions/{name}")
async def read_impression(name: str, _auth: None = Depends(require_bot_token)):
    impression = impression_service.get(name)
    if not impression:
        raise HTTPException(status_code=404, detail="Person impression not found")
    return impression.__dict__


@app.post("/api/v1/impressions/write")
async def write_impression(payload: ImpressionWriteRequest, _auth: None = Depends(require_bot_token)):
    saved = impression_service.save(
        PersonImpression(
            name=payload.name.strip(),
            summary=payload.summary.strip(),
            traits=payload.traits,
            interests=payload.interests,
            preferences=payload.preferences,
            relationship=payload.relationship.strip(),
            evidence_dates=payload.evidence_dates,
            confidence=payload.confidence,
            notes=payload.notes.strip(),
        )
    )
    return {"status": "ok", "item": saved.__dict__}
