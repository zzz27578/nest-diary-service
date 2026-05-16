from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import DiaryEntry, PersonImpression, ServiceUiSettings
from app.web_auth import WebSessionAuth

WEB_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))


def create_web_router(
    auth: WebSessionAuth,
    diary_service=None,
    media_service=None,
    revision_service=None,
    impression_service=None,
    settings_store=None,
    security_store=None,
    web_auth=None,
    version_service=None,
    runtime_settings=None,
) -> APIRouter:
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
                "people_count": len(impression_service.list_people()) if impression_service else 0,
                "recent_entries": entries[:5],
                "active": "dashboard",
                "archive": diary_service.archive_tree() if diary_service else [],
            },
        )

    @router.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse(request, "login.html", {"error": "", "default_password": "12345678"})

    @router.post("/login")
    async def login(request: Request, password: str = Form(...)):
        if not auth.verify_password(password):
            return templates.TemplateResponse(
                request,
                "login.html",
                {"error": "密码不对", "default_password": "12345678"},
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

    @router.get("/write", response_class=HTMLResponse)
    async def write_page(request: Request, date: str = "", saved: str = "", error: str = ""):
        redirect = require_login(request)
        if redirect:
            return redirect
        selected_entry = None
        if date and diary_service:
            try:
                selected_entry = diary_service.read_by_date(date)
            except FileNotFoundError:
                error = error or f"{date} 没有找到日记"
        return templates.TemplateResponse(
            request,
            "write.html",
            {
                "selected_entry": selected_entry,
                "saved": saved,
                "error": error,
                "active": "write",
                "ui_settings": settings_store.load() if settings_store else ServiceUiSettings(),
            },
        )

    @router.get("/search", response_class=HTMLResponse)
    async def search_page(request: Request, q: str = ""):
        redirect = require_login(request)
        if redirect:
            return redirect
        ui_settings = settings_store.load() if settings_store else ServiceUiSettings()
        results = diary_service.search(q, top_k=ui_settings.search_default_top_k) if q and diary_service else []
        return templates.TemplateResponse(
            request,
            "search.html",
            {
                "q": q,
                "results": results,
                "active": "search",
                "archive": diary_service.archive_tree() if diary_service else [],
            },
        )

    @router.get("/diary", response_class=HTMLResponse)
    async def diary_page(request: Request, date: str = "", error: str = ""):
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
        elif entries:
            selected_entry = entries[0]
        return templates.TemplateResponse(
            request,
            "diary.html",
            {
                "entries": entries,
                "selected_entry": selected_entry,
                "error": error,
                "active": "diary",
                "archive": diary_service.archive_tree() if diary_service else [],
            },
        )

    @router.get("/media", response_class=HTMLResponse)
    async def media_page(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        manifests = media_service.list_manifests() if media_service else []
        return templates.TemplateResponse(
            request,
            "media.html",
            {"manifests": manifests, "active": "media"},
        )

    @router.get("/revisions", response_class=HTMLResponse)
    async def revisions_page(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        revisions = revision_service.list_revisions() if revision_service else []
        return templates.TemplateResponse(
            request,
            "revisions.html",
            {"revisions": revisions, "active": "revisions"},
        )

    @router.get("/impressions", response_class=HTMLResponse)
    async def impressions_page(request: Request, name: str = "", saved: str = "", error: str = ""):
        redirect = require_login(request)
        if redirect:
            return redirect
        people = impression_service.list_people() if impression_service else []
        selected_person = impression_service.get(name) if name and impression_service else None
        if name and not selected_person:
            error = error or f"{name} 没有找到人物印象"
        return templates.TemplateResponse(
            request,
            "impressions.html",
            {
                "people": people,
                "selected_person": selected_person,
                "saved": saved,
                "error": error,
                "active": "impressions",
            },
        )

    @router.get("/settings", response_class=HTMLResponse)
    async def settings_page(
        request: Request,
        saved: str = "",
        error: str = "",
        version_message: str = "",
        version_current: str = "",
        version_latest: str = "",
        update_available: str = "",
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        ui_settings = settings_store.load() if settings_store else ServiceUiSettings()
        security = security_store.load() if security_store else None
        return templates.TemplateResponse(
            request,
            "settings.html",
            {
                "settings": ui_settings,
                "security": security,
                "runtime_settings": runtime_settings,
                "version_service": version_service,
                "version_message": version_message,
                "version_current": version_current,
                "version_latest": version_latest,
                "update_available": update_available,
                "saved": saved,
                "error": error,
                "active": "settings",
            },
        )

    @router.get("/panel", response_class=HTMLResponse)
    async def panel_redirect():
        return RedirectResponse("/write", status_code=303)

    @router.post("/write/diary")
    async def save_diary(
        request: Request,
        date: str = Form(...),
        title: str = Form(""),
        body: str = Form(...),
        mood: str = Form(""),
        tags: str = Form(""),
        people: str = Form(""),
        media_refs: str = Form(""),
        importance: int = Form(3),
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not diary_service:
            return RedirectResponse("/write?error=diary-service-unavailable", status_code=303)
        entry = DiaryEntry(
            date=date.strip(),
            title=title.strip() or None,
            body=body.strip(),
            mood=_split_words(mood),
            tags=_split_words(tags),
            people=_split_words(people),
            media_refs=_split_lines(media_refs),
            importance=max(1, min(int(importance), 5)),
            source="admin",
        )
        diary_service.write_diary(entry, reason="web_admin_update")
        return RedirectResponse(f"/write?date={entry.date}&saved=1", status_code=303)

    @router.post("/panel/diary")
    async def save_diary_legacy(request: Request):
        return RedirectResponse("/write", status_code=303)

    @router.post("/impressions")
    async def save_impression(
        request: Request,
        name: str = Form(...),
        summary: str = Form(...),
        traits: str = Form(""),
        interests: str = Form(""),
        preferences: str = Form(""),
        relationship: str = Form(""),
        evidence_dates: str = Form(""),
        confidence: int = Form(3),
        notes: str = Form(""),
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not impression_service:
            return RedirectResponse("/impressions?error=impression-service-unavailable", status_code=303)
        item = PersonImpression(
            name=name.strip(),
            summary=summary.strip(),
            traits=_split_words(traits),
            interests=_split_words(interests),
            preferences=_split_words(preferences),
            relationship=relationship.strip(),
            evidence_dates=_split_words(evidence_dates),
            confidence=max(1, min(int(confidence), 5)),
            notes=notes.strip(),
        )
        impression_service.save(item)
        return RedirectResponse(f"/impressions?name={item.name}&saved=1", status_code=303)

    @router.post("/settings")
    async def save_settings(
        request: Request,
        search_default_top_k: int = Form(20),
        diary_archive_granularity: str = Form("day"),
        allow_media_refs: str = Form(""),
        show_impression_prompt: str = Form(""),
        impression_prompt: str = Form(""),
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not settings_store:
            return RedirectResponse("/settings?error=settings-store-unavailable", status_code=303)
        settings_store.save(
            ServiceUiSettings(
                search_default_top_k=search_default_top_k,
                diary_archive_granularity=diary_archive_granularity,
                allow_media_refs=allow_media_refs == "on",
                show_impression_prompt=show_impression_prompt == "on",
                impression_prompt=impression_prompt.strip(),
            )
        )
        return RedirectResponse("/settings?saved=1", status_code=303)

    @router.post("/settings/security")
    async def save_security_settings(
        request: Request,
        admin_password: str = Form(""),
        bot_api_token: str = Form(""),
        generate_bot_api_token: str = Form(""),
    ):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not security_store:
            return RedirectResponse("/settings?error=security-store-unavailable", status_code=303)
        token = security_store.generate_token() if generate_bot_api_token == "on" else bot_api_token.strip()
        saved_security = security_store.update(
            admin_password=admin_password.strip() or None,
            bot_api_token=token,
        )
        if web_auth:
            web_auth.admin_password = saved_security.admin_password
            web_auth.session_secret = saved_security.bot_api_token or "development-session-secret"
        return RedirectResponse("/settings?saved=1", status_code=303)

    @router.post("/settings/version/check")
    async def check_version(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not version_service:
            return RedirectResponse("/settings?error=version-service-unavailable", status_code=303)
        try:
            result = version_service.check_latest()
            message = "发现新版本。" if result.update_available else "当前已经是最新版本。"
            return RedirectResponse(
                "/settings?"
                f"version_message={quote(message)}"
                f"&version_current={quote(result.current)}"
                f"&version_latest={quote(result.latest)}"
                f"&update_available={'1' if result.update_available else '0'}",
                status_code=303,
            )
        except Exception as exc:
            return RedirectResponse(f"/settings?error={quote('版本检测失败：' + str(exc))}", status_code=303)

    @router.post("/settings/version/update")
    async def update_version(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        if not version_service:
            return RedirectResponse("/settings?error=version-service-unavailable", status_code=303)
        result = version_service.update()
        target = "version_message" if result.ok else "error"
        detail = result.message
        if result.output:
            detail = f"{detail}\n{result.output}"
        return RedirectResponse(f"/settings?{target}={quote(detail)}", status_code=303)

    return router


def mount_static(app) -> None:
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")


def _split_words(value: str) -> list[str]:
    normalized = value.replace("，", ",").replace("、", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _split_lines(value: str) -> list[str]:
    return [item.strip() for item in value.splitlines() if item.strip()]
