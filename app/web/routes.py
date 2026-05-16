from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import DiaryEntry
from app.web_auth import WebSessionAuth

WEB_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))


def create_web_router(auth: WebSessionAuth, diary_service=None, media_service=None, revision_service=None) -> APIRouter:
    router = APIRouter()

    def require_login(request: Request):
        redirect = auth.redirect_if_missing(request.cookies.get("nest_session"))
        return redirect

    @router.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        entries = diary_service.list_entries() if diary_service else []
        media = media_service.list_manifests() if media_service else []
        revisions = revision_service.list_revisions() if revision_service else []
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "entries_count": len(entries),
                "media_count": sum(len(item.get("assets", [])) for item in media),
                "revisions_count": len(revisions),
                "recent_entries": entries[:5],
            },
        )

    @router.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse(request, "login.html", {"error": ""})

    @router.post("/login")
    async def login(request: Request, password: str = Form(...)):
        if not auth.verify_password(password):
            return templates.TemplateResponse(
                request,
                "login.html",
                {"error": "密码不对"},
                status_code=401,
            )
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("nest_session", auth.create_session_token(), httponly=True, samesite="lax")
        return response

    @router.post("/logout")
    async def logout():
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie("nest_session")
        return response

    @router.get("/panel", response_class=HTMLResponse)
    async def panel(request: Request, q: str = "", date: str = "", saved: str = "", error: str = ""):
        redirect = require_login(request)
        if redirect:
            return redirect
        entries = diary_service.list_entries() if diary_service else []
        selected_entry = None
        if date and diary_service:
            try:
                selected_entry = diary_service.read_by_date(date)
            except FileNotFoundError:
                error = error or f"{date} 没有找到日记"
        results = diary_service.search(q, top_k=20) if q and diary_service else []
        manifests = media_service.list_manifests() if media_service else []
        revisions = revision_service.list_revisions() if revision_service else []
        return templates.TemplateResponse(
            request,
            "panel.html",
            {
                "entries": entries,
                "selected_entry": selected_entry,
                "q": q,
                "results": results,
                "manifests": manifests,
                "revisions": revisions,
                "saved": saved,
                "error": error,
            },
        )

    @router.post("/panel/diary")
    async def save_diary(
        request: Request,
        date: str = Form(...),
        title: str = Form(""),
        body: str = Form(...),
        mood: str = Form(""),
        tags: str = Form(""),
        people: str = Form(""),
        importance: int = Form(3),
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not diary_service:
            return RedirectResponse("/panel?error=diary-service-unavailable#editor", status_code=303)
        entry = DiaryEntry(
            date=date.strip(),
            title=title.strip() or None,
            body=body.strip(),
            mood=_split_words(mood),
            tags=_split_words(tags),
            people=_split_words(people),
            importance=max(1, min(int(importance), 5)),
            source="admin",
        )
        diary_service.write_diary(entry, reason="web_admin_update")
        return RedirectResponse(f"/panel?date={entry.date}&saved=1#diary", status_code=303)

    return router


def mount_static(app) -> None:
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


def _split_words(value: str) -> list[str]:
    normalized = value.replace("，", ",").replace("、", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]
