# 小窝日记服务

仓库地址：<https://github.com/zzz27578/nest-diary-service>

这是小窝日记系统的本体服务。它独立于 AstrBot 运行，负责网站、API、日记存储、媒体存储、搜索索引、版本追溯、旧日记迁移和归档。

对应 AstrBot 连接插件：<https://github.com/zzz27578/astrbot-plugin-nest-diary-connector>

## 当前已实现

- Bot token API：`/api/v1/status`
- 日记写入：`/api/v1/diary/write`
- 日记读取：`/api/v1/diary/{date}`
- 日记搜索：`/api/v1/diary/search`
- 日记归档：`/api/v1/diary/archive`
- 媒体归档：`/api/v1/media/attach`
- 按日期读取媒体：`/api/v1/media/by-date/{date}`
- 媒体 blob 访问：`/media/blobs/{sha256}`
- 人物印象列表：`/api/v1/impressions`
- 人物印象读取：`/api/v1/impressions/{name}`
- 人物印象写入：`/api/v1/impressions/write`
- Markdown 日记落盘
- 日记按 `diary/YYYY/MM/YYYY-MM-DD.md` 归档
- JSON 人物印象落盘
- SQLite FTS5 + 中文 LIKE fallback 搜索
- 覆盖写入前 revision 快照
- SHA256 内容寻址媒体仓库
- 密码保护网页后台
- 后台真实路由：`/`、`/write`、`/search`、`/diary`、`/impressions`、`/media`、`/revisions`、`/settings`
- 普通 Docker Compose 部署
- 可选 1Panel 本地应用包

## 普通 Docker 部署

复制环境变量文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
NEST_PORT=28080
NEST_ADMIN_PASSWORD=12345678
NEST_BOT_API_TOKEN=
TZ=Asia/Shanghai
```

如果不填环境变量，网页初始管理员密码也是 `12345678`。第一次登录后请到 `/settings` 修改管理员密码，并生成或填写 `Bot API Token`。

启动：

```bash
docker compose up -d
```

默认端口是 `28080`。日记、媒体、索引和修订记录会保存在当前目录的 `data/` 中。

## 本地网页精修

本项目现在提供两种本地查看方式，按用途选择：

- 只看设计、改布局、改颜色：直接双击打开仓库根目录的 `webui-prototype.html`。
- 看真实登录、真实写入、真实搜索：用 Python 跑本地服务，然后打开 `http://127.0.0.1:28080`。

`webui-prototype.html` 是静态预览页，不需要后端请求，所以双击就能看。它复用真实页面的 `app/web/static/app.css` 和图片资源，用来快速打磨界面。

如果要确认“服务器上最终跑出来的真实页面”，就需要启动本地 Python 服务。这样本地修改 `app/web/templates/`、`app/web/static/` 后刷新浏览器就能看到，和服务器运行的页面来源一致。

PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:NEST_DATA_DIR = "data-dev"
$env:NEST_ADMIN_PASSWORD = "dev-password"
$env:NEST_BOT_API_TOKEN = "dev-token-change-me"
uvicorn app.main:app --reload --host 127.0.0.1 --port 28080
```

打开：

```text
http://127.0.0.1:28080
```

登录密码是上面设置的 `dev-password`。开发数据会落在 `data-dev/`，不会污染正式 `data/`。

检查服务：

```bash
curl -H "Authorization: Bearer 你的token" http://127.0.0.1:28080/api/v1/status
```

## AstrBot 连接

在 AstrBot 连接插件中配置：

```text
service_url = http://nest-diary:28080
bot_api_token = 与 NEST_BOT_API_TOKEN 相同
```

更直观的绑定方式：

1. 先登录小窝网页后台，初始密码 `12345678`。
2. 打开 `/settings`，修改管理员密码。
3. 在“访问密钥”里生成或填写 `Bot API Token`。
4. 把这串 token 复制到 AstrBot 插件配置的 `bot_api_token`。
5. 插件里的 `service_url` 填小窝服务地址，例如 `http://nest-diary:28080`。

管理员密码只管网页登录；`Bot API Token` 只管 AstrBot 插件访问 API。两者不要混用。

如果两个容器不在同一个 Docker 网络，可以改成宿主机或反代地址。

## 1Panel 本地应用支持

1Panel 本地应用包位于：

```text
deploy/1panel/nest-diary/
```

它使用镜像：

```text
ghcr.io/zzz27578/nest-diary-service:0.2.0
```

1Panel 只是可选部署方式；不使用 1Panel 时，直接使用本项目根目录的 `docker-compose.yml` 即可。

## 图片规范

服务内置资源：

```text
app/web/static/nest-avatar.png
app/web/static/nest-og.png
deploy/1panel/nest-diary/logo.png
```

其中 1Panel 图标是 1:1 的 `logo.png`，网页头像用于后台首页展示。

## 本地 WebUI 原型

为了方便直接改前端，仓库根目录提供了一个可直接打开的静态原型：

```text
webui-prototype.html
```

打开方式：

```text
C:\Users\29505\Desktop\记忆插件\nest-diary-service\webui-prototype.html
```

它不需要启动服务，直接用浏览器打开就能看到小窝后台雏形。这个文件用于快速调整视觉和布局；真正运行时的服务端模板在：

```text
app/web/templates/
app/web/static/
```

需要注意：静态原型只负责“看起来像真实页面”，不会真的登录、写日记或搜索。要测试真实功能，请使用“本地网页精修”里的 Python 服务方式。

## 人物印象

人物印象是日记之外的长期认识层，数据保存在：

```text
data/memory/people/
```

推荐让 bot 在写完日记后自行判断是否需要更新人物印象。只有当日记里出现稳定证据时才更新，例如性格特征、兴趣爱好、偏好、关系变化、长期需求或重要边界。没有新证据时不需要硬写。

## 数据存储结构

默认数据目录是容器内 `/app/data`，也可以通过 `NEST_DATA_DIR` 改到别处。核心结构如下：

```text
data/
  diary/YYYY/MM/YYYY-MM-DD.md          # 每日 Markdown 日记，带 frontmatter
  memory/people/*.json                # 人物印象 JSON
  media/blobs/sha256/aa/bb/<hash>.*   # 内容寻址媒体原件
  media/by-date/YYYY/MM/YYYY-MM-DD/manifest.json
  revisions/diary/YYYY/MM/YYYY-MM-DD/*.md
  index/nest.sqlite                   # 搜索索引，可重建
  settings/service-ui.json            # 本体网页设置
  settings/security.json              # 管理员密码和 Bot API Token
```

不丢数据的关键：

- 把整个 `data/` 目录映射到 Docker volume 或宿主机目录。
- 日记和人物印象是普通文本文件，方便备份和人工检查。
- 同日期覆盖写入前会写入 `revisions/` 快照。
- 媒体用 SHA256 内容寻址，同一文件不会重复存。
- SQLite 只是检索索引，坏了可以从 Markdown 日记重建，不是唯一数据源。

日记支持 `media_refs` 字段，可保存图片或附件 URL。先通过 `attach_media` 归档文件，再把返回的 `/media/blobs/{sha256}` 写入日记，就能在网页日记页显示或跳转。

## 使用手册

见：

```text
docs/使用手册.md
```
