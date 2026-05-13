# Nest Diary Dual Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $superpower-subagents (recommended) or $superpower-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking via update_plan.

**Goal:** Build Nest Diary as two independently installable projects: a standard AstrBot connector plugin and a standalone private diary service with optional 1Panel local-app packaging.

**Architecture:** The AstrBot plugin is a lightweight connector that gives the bot tools, skills, configuration, and a stable "doorplate" to its nest. The standalone service owns the web panel, API, Markdown diary storage, content-addressed media storage, SQLite indexes, revisions, migration, and archiving. They communicate over an internal HTTP API using a bot token.

**Tech Stack:** AstrBot plugin APIs for the connector; Python FastAPI service for the nest body; Markdown with front matter for diary source-of-truth; SQLite + FTS5 for metadata and full-text search; SHA256 content-addressed local media storage; Docker Compose for generic deployment; optional 1Panel local application package.

---

## Workspace Split

This workspace contains two subprojects that should be easy to split into two separate repositories later:

```text
C:\Users\29505\Desktop\记忆插件\
  astrbot-plugin-nest-diary-connector\
    # Future standalone repo: standard AstrBot plugin.

  nest-diary-service\
    # Future standalone repo: private nest service and optional deployment packages.

  docs\
    superpowers\plans\
      2026-05-13-nest-diary-dual-project.md
```

## Hard Requirements

- Keep the connector plugin and service installable independently.
- The connector plugin must follow standard AstrBot plugin shape, so users can install it like a normal AstrBot plugin.
- The service must not require 1Panel. 1Panel is only one optional packaging target.
- The bot must not operate the web UI like a human. It must use connector tools that call service APIs.
- The service must provide a bot-only API authenticated by `NEST_BOT_API_TOKEN`.
- The web panel must be password protected separately from the bot token.
- The bot has full autonomy to create, revise, archive, reorganize, and enrich diary content through tools.
- Full autonomy must still be traceable: every mutation records time, reason, source, and a recoverable revision.
- Persona prompts are not hardcoded. AstrBot's native persona injection remains responsible for character/personality.
- Diary writing must be subjective and reflective, not a raw chat log.
- Diary lookup must never read all diary files by default.
- Diary storage must remain human-readable and physically organized by year, month, and date.
- Images, audio, and attachments must be first-class stored evidence.
- Legacy import must support `/AstrBot/data/daily_diary.txt`, including both `[YYYY-MM-DD HH:mm CST]` blocks and `YYYY-MM-DD:` / `YYYY-MM-DD：` inline entries.

## Runtime Connection Model

```text
AstrBot container
  astrbot_plugin_nest_diary_connector
    - stores service URL
    - stores bot API token
    - exposes bot tools and built-in skills
    - forwards operations to service

Nest Diary service container
  FastAPI API
  password-protected web panel
  Markdown diary storage
  media blob storage
  SQLite indexes
```

Connector config:

```text
NEST_SERVICE_URL=http://nest-diary:28080
NEST_BOT_API_TOKEN=<long random token>
REQUEST_TIMEOUT_SECONDS=30
DAILY_WRITE_ENABLED=true
NOTIFY_AFTER_WRITE=true
```

Service config:

```text
NEST_BOT_API_TOKEN=<same long random token>
NEST_ADMIN_PASSWORD=<web login password>
NEST_DATA_DIR=/app/data
TZ=Asia/Shanghai
```

Bot API examples:

```text
GET  /api/v1/status
POST /api/v1/diary/write
GET  /api/v1/diary/search
GET  /api/v1/diary/{date}
POST /api/v1/diary/revise
POST /api/v1/archive/run
POST /api/v1/media/upload
GET  /api/v1/skills
POST /api/v1/skills/reload
```

Each mutating call includes:

```json
{
  "actor": "astrbot",
  "intent": "daily_diary_write",
  "reason": "scheduled daily diary workflow",
  "idempotency_key": "2026-05-13-daily-write"
}
```

## Service Data Storage Scheme

The service owns all heavy data:

```text
nest-diary-service/data/
  diary/
    2026/
      05/
        2026-05-13.md
  memory/
    people/
    topics/
    events/
  archive/
    monthly/
    yearly/
  media/
    blobs/
      sha256/
        ab/
          cd/
            abcd1234....png
    variants/
    by-date/
      2026/
        05/
          2026-05-13/
            manifest.json
  drafts/
  revisions/
  imports/
  logs/
  index/
    nest.sqlite
```

Markdown is source-of-truth for diary text. SQLite stores metadata and FTS indexes. Media is content-addressed by SHA256, with date manifests linking assets to diary entries.

## Connector Project Layout

```text
astrbot-plugin-nest-diary-connector/
  astrbot_plugin_nest_diary_connector/
    main.py
    metadata.yaml
    _conf_schema.json
    client.py
    tools.py
    scheduler.py
    skills/
      diary_write.md
      diary_access.md
      diary_archive.md
      diary_emotion_review.md
      diary_memory_extract.md
  README.md
```

## Service Project Layout

```text
nest-diary-service/
  app/
    main.py
    config.py
    auth.py
    models.py
    paths.py
    diary/
      markdown_store.py
      diary_service.py
      migration_service.py
      revision_service.py
    search/
      search_service.py
    media/
      media_service.py
    archive/
      archive_service.py
    web/
      routes.py
      templates/
      static/
  tests/
  Dockerfile
  docker-compose.yml
  .env.example
  README.md
  deploy/
    1panel/
      nest-diary/
        logo.png
        data.yml
        README.md
        0.1.0/
          data.yml
          docker-compose.yml
          .env.sample
```

---

### Task 1: Initialize Both Subprojects

**Files:**
- Create: `astrbot-plugin-nest-diary-connector/README.md`
- Create: `nest-diary-service/README.md`
- Create: `nest-diary-service/.env.example`

- [ ] **Step 1: Create connector README**

Create `astrbot-plugin-nest-diary-connector/README.md`:

```markdown
# AstrBot Nest Diary Connector

Standard AstrBot plugin that gives the bot native tools and skills for operating its private Nest Diary service.

This plugin does not store diary text or media. It only stores lightweight connector configuration and calls the Nest Diary service API.
```

- [ ] **Step 2: Create service README**

Create `nest-diary-service/README.md`:

```markdown
# Nest Diary Service

Standalone private diary/blog nest service for AstrBot.

It provides the password-protected web panel, bot API, Markdown diary storage, content-addressed media storage, SQLite search indexes, revisions, migration, and archives.

1Panel packaging is optional. The service can also run with plain Docker Compose.
```

- [ ] **Step 3: Create service env sample**

Create `nest-diary-service/.env.example`:

```dotenv
NEST_HOST=0.0.0.0
NEST_PORT=28080
NEST_DATA_DIR=/app/data
NEST_ADMIN_PASSWORD=change-me
NEST_BOT_API_TOKEN=change-me-to-a-long-random-token
TZ=Asia/Shanghai
```

### Task 2: Build Standard AstrBot Connector Skeleton

**Files:**
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/main.py`
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/metadata.yaml`
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/_conf_schema.json`
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/client.py`

- [ ] **Step 1: Create plugin metadata**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/metadata.yaml`:

```yaml
name: astrbot_plugin_nest_diary_connector
desc: Connector plugin for operating a standalone Nest Diary service through bot-native tools.
help: Configure service URL and bot API token, then use the provided diary tools and skills.
version: v0.1.0
author: local
repo: ""
```

- [ ] **Step 2: Create plugin config schema**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/_conf_schema.json`:

```json
{
  "service_url": {
    "description": "Nest Diary service URL, for example http://nest-diary:28080.",
    "type": "string",
    "default": "http://nest-diary:28080"
  },
  "bot_api_token": {
    "description": "Bot API token configured in the Nest Diary service.",
    "type": "string",
    "default": ""
  },
  "request_timeout_seconds": {
    "description": "HTTP request timeout in seconds.",
    "type": "int",
    "default": 30
  },
  "daily_write_enabled": {
    "description": "Enable connector-side scheduled daily diary trigger.",
    "type": "bool",
    "default": true
  },
  "notify_after_write": {
    "description": "Send notification after daily diary workflow.",
    "type": "bool",
    "default": true
  }
}
```

- [ ] **Step 3: Create HTTP client**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/client.py`:

```python
import aiohttp


class NestDiaryClient:
    def __init__(self, service_url: str, token: str, timeout_seconds: int = 30):
        self.service_url = service_url.rstrip("/")
        self.token = token
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    async def status(self) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(f"{self.service_url}/api/v1/status", headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def write_diary(self, payload: dict) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(f"{self.service_url}/api/v1/diary/write", json=payload, headers=self._headers()) as response:
                response.raise_for_status()
                return await response.json()

    async def search_diary(self, query: str, top_k: int = 8) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(
                f"{self.service_url}/api/v1/diary/search",
                params={"q": query, "top_k": top_k},
                headers=self._headers(),
            ) as response:
                response.raise_for_status()
                return await response.json()
```

- [ ] **Step 4: Create plugin entrypoint**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/main.py`:

```python
from astrbot.api.event import filter
from astrbot.api.star import Context, Star, register

from .client import NestDiaryClient


@register("astrbot_plugin_nest_diary_connector", "local", "Nest Diary connector plugin.", "0.1.0")
class NestDiaryConnectorPlugin(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config or {}
        self.client = NestDiaryClient(
            service_url=self.config.get("service_url", "http://nest-diary:28080"),
            token=self.config.get("bot_api_token", ""),
            timeout_seconds=int(self.config.get("request_timeout_seconds", 30)),
        )

    @filter.command("小窝状态")
    async def nest_status(self, event):
        try:
            status = await self.client.status()
            message = f"小窝在线：{status.get('status', 'unknown')}"
        except Exception as exc:
            message = f"小窝暂时连不上：{exc}"
        yield event.plain_result(message)
```

### Task 3: Add Connector Skills

**Files:**
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_write.md`
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_access.md`
- Create: `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_archive.md`

- [ ] **Step 1: Create diary write skill**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_write.md`:

```markdown
# diary-write

Use Nest Diary tools to write subjective daily diary entries. Do not write raw chat logs. Include what happened, personal evaluation, emotion, durable memory about 老爸, and follow-up clues.
```

- [ ] **Step 2: Create diary access skill**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_access.md`:

```markdown
# diary-access

Use Nest Diary search tools before reading diary content. Never request or read the entire diary corpus by default. If a date is known, read that date. If keywords are known, search first and open only the most relevant entries.
```

- [ ] **Step 3: Create diary archive skill**

Create `astrbot-plugin-nest-diary-connector/astrbot_plugin_nest_diary_connector/skills/diary_archive.md`:

```markdown
# diary-archive

Maintain monthly, yearly, topic, person, and event archives through Nest Diary tools. Keep source dates linked and never erase original diary evidence.
```

### Task 4: Build Service Skeleton

**Files:**
- Create: `nest-diary-service/app/main.py`
- Create: `nest-diary-service/app/config.py`
- Create: `nest-diary-service/app/auth.py`
- Create: `nest-diary-service/app/paths.py`
- Create: `nest-diary-service/pyproject.toml`

- [ ] **Step 1: Create service package config**

Create `nest-diary-service/pyproject.toml`:

```toml
[project]
name = "nest-diary-service"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "python-multipart>=0.0.9"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create config loader**

Create `nest-diary-service/app/config.py`:

```python
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    admin_password: str
    bot_api_token: str
    host: str
    port: int


def load_settings() -> Settings:
    return Settings(
        data_dir=Path(os.getenv("NEST_DATA_DIR", "/app/data")),
        admin_password=os.getenv("NEST_ADMIN_PASSWORD", ""),
        bot_api_token=os.getenv("NEST_BOT_API_TOKEN", ""),
        host=os.getenv("NEST_HOST", "0.0.0.0"),
        port=int(os.getenv("NEST_PORT", "28080")),
    )
```

- [ ] **Step 3: Create token auth**

Create `nest-diary-service/app/auth.py`:

```python
from fastapi import Header, HTTPException


def verify_bot_token(expected_token: str, authorization: str | None = Header(default=None)) -> None:
    if not expected_token:
        raise HTTPException(status_code=503, detail="Bot API token is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bot token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid bot token")
```

- [ ] **Step 4: Create service API**

Create `nest-diary-service/app/main.py`:

```python
from fastapi import Depends, FastAPI

from .auth import verify_bot_token
from .config import load_settings

settings = load_settings()
app = FastAPI(title="Nest Diary Service")


def require_bot():
    verify_bot_token(settings.bot_api_token)


@app.get("/api/v1/status")
async def status(_auth=Depends(require_bot)):
    return {"status": "ok", "service": "nest-diary"}
```

### Task 5: Implement Service Storage Foundation

**Files:**
- Create: `nest-diary-service/app/paths.py`
- Create: `nest-diary-service/app/models.py`
- Create: `nest-diary-service/app/diary/markdown_store.py`
- Test: `nest-diary-service/tests/test_paths.py`

- [ ] **Step 1: Create path tests**

Create `nest-diary-service/tests/test_paths.py`:

```python
from app.paths import NestPaths


def test_diary_paths_are_year_month_date(tmp_path):
    paths = NestPaths(tmp_path)
    paths.ensure_all()

    assert paths.diary_file("2026-05-13") == tmp_path / "diary" / "2026" / "05" / "2026-05-13.md"
    assert (tmp_path / "media" / "blobs" / "sha256").is_dir()
    assert (tmp_path / "index").is_dir()
```

- [ ] **Step 2: Implement paths**

Create `nest-diary-service/app/paths.py`:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NestPaths:
    root: Path

    def diary_file(self, date: str) -> Path:
        year, month, _day = date.split("-")
        return self.root / "diary" / year / month / f"{date}.md"

    def ensure_all(self) -> None:
        for path in [
            self.root / "diary",
            self.root / "memory" / "people",
            self.root / "memory" / "topics",
            self.root / "memory" / "events",
            self.root / "archive" / "monthly",
            self.root / "archive" / "yearly",
            self.root / "media" / "blobs" / "sha256",
            self.root / "media" / "variants",
            self.root / "media" / "by-date",
            self.root / "drafts",
            self.root / "revisions",
            self.root / "imports",
            self.root / "logs",
            self.root / "index",
        ]:
            path.mkdir(parents=True, exist_ok=True)
```

### Task 6: Implement Service Diary, Search, Revisions, and Media

**Files:**
- Create: `nest-diary-service/app/diary/diary_service.py`
- Create: `nest-diary-service/app/diary/migration_service.py`
- Create: `nest-diary-service/app/diary/revision_service.py`
- Create: `nest-diary-service/app/search/search_service.py`
- Create: `nest-diary-service/app/media/media_service.py`
- Test: `nest-diary-service/tests/test_legacy_migration.py`
- Test: `nest-diary-service/tests/test_search_service.py`
- Test: `nest-diary-service/tests/test_media_service.py`

- [ ] **Step 1: Implement these using the approved storage rules**

Implementation must preserve these decisions:

```text
Markdown files are source-of-truth.
SQLite FTS5 is the first full-text search backend.
Media blobs are stored by SHA256.
Revisions are saved before mutation.
Legacy parser handles bracket dates and inline dates.
```

- [ ] **Step 2: Verify with focused tests**

Run:

```bash
pytest nest-diary-service/tests -v
```

Expected: all service tests pass.

### Task 7: Add Service Web Panel and Generic Docker Deployment

**Files:**
- Create: `nest-diary-service/app/web/routes.py`
- Create: `nest-diary-service/app/web/templates/login.html`
- Create: `nest-diary-service/app/web/templates/dashboard.html`
- Create: `nest-diary-service/app/web/static/app.css`
- Create: `nest-diary-service/Dockerfile`
- Create: `nest-diary-service/docker-compose.yml`

- [ ] **Step 1: Build password-protected web shell**

The web shell must require `NEST_ADMIN_PASSWORD` and must not expose diary data before login.

- [ ] **Step 2: Build generic Docker deployment**

Create a deployment that works without 1Panel:

```yaml
services:
  nest-diary:
    build: .
    restart: unless-stopped
    ports:
      - "${NEST_PORT:-28080}:28080"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

### Task 8: Add Optional 1Panel Local App Package

**Files:**
- Create: `nest-diary-service/deploy/1panel/nest-diary/README.md`
- Create: `nest-diary-service/deploy/1panel/nest-diary/data.yml`
- Create: `nest-diary-service/deploy/1panel/nest-diary/0.1.0/data.yml`
- Create: `nest-diary-service/deploy/1panel/nest-diary/0.1.0/docker-compose.yml`
- Create: `nest-diary-service/deploy/1panel/nest-diary/0.1.0/.env.sample`

- [ ] **Step 1: Create optional package only**

The package must be documented as optional. The service must remain installable with plain Docker Compose.

- [ ] **Step 2: Keep data volume inside the app install directory**

The 1Panel compose must map:

```text
./data:/app/data
```

so 1Panel backup and restore can capture the nest data.

### Task 9: Final Verification

**Files:**
- Modify as needed based on verification failures.

- [ ] **Step 1: Verify connector compiles**

Run:

```bash
python -m compileall astrbot-plugin-nest-diary-connector
```

Expected: no syntax errors.

- [ ] **Step 2: Verify service tests**

Run:

```bash
pytest nest-diary-service/tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Verify architecture boundaries**

Check:

```text
Connector contains no heavy diary or media storage.
Connector can be installed as a normal AstrBot plugin.
Service can run without AstrBot using Docker Compose.
1Panel package is optional and lives under service deploy files.
Bot access uses API token.
Web access uses administrator password.
Diary text lives in Markdown files.
Media uses content-addressed storage.
Search never requires full diary reads by default.
```

Expected: every item is true.

---

## Approval Notes

This replaces the earlier single-plugin plan. The intended future release shape is two repositories:

```text
astrbot-plugin-nest-diary-connector
nest-diary-service
```

The current workspace keeps them as two sibling folders only for convenience while designing and building.

## Next Skill

After approval, implementation should use `$superpower-executing-plans` for inline execution or `$superpower-subagents` for task-by-task delegated execution.
