from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
            "dashboard.html",
            {
                "request": request,
                "entries_count": len(entries),
                "media_count": sum(len(item.get("assets", [])) for item in media),
                "revisions_count": len(revisions),
                "recent_entries": entries[:5],
            },
        )

    @router.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request, "error": ""})

    @router.post("/login")
    async def login(request: Request, password: str = Form(...)):
        if not auth.verify_password(password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "密码不对"},
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

    @router.get("/diary", response_class=HTMLResponse)
    async def diary_list(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        entries = diary_service.list_entries() if diary_service else []
        return templates.TemplateResponse("diary.html", {"request": request, "entries": entries})

    @router.get("/diary/{date}", response_class=HTMLResponse)
    async def diary_detail(request: Request, date: str):
        redirect = require_login(request)
        if redirect:
            return redirect
        entry = diary_service.read_by_date(date)
        return templates.TemplateResponse("diary_detail.html", {"request": request, "entry": entry})

    @router.get("/search", response_class=HTMLResponse)
    async def search_page(request: Request, q: str = ""):
        redirect = require_login(request)
        if redirect:
            return redirect
        results = diary_service.search(q, top_k=20) if q and diary_service else []
        return templates.TemplateResponse("search.html", {"request": request, "q": q, "results": results})

    @router.get("/media", response_class=HTMLResponse)
    async def media_page(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        manifests = media_service.list_manifests() if media_service else []
        return templates.TemplateResponse("media.html", {"request": request, "manifests": manifests})

    @router.get("/revisions", response_class=HTMLResponse)
    async def revisions_page(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect
        revisions = revision_service.list_revisions() if revision_service else []
        return templates.TemplateResponse("revisions.html", {"request": request, "revisions": revisions})

    return router


def mount_static(app) -> None:
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")
