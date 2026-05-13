# 小窝日记服务

仓库地址：<https://github.com/zzz27578/nest-diary-service>

这是小窝日记系统的本体服务。它独立于 AstrBot 运行，负责网站、API、日记存储、媒体存储、搜索索引、版本追溯、旧日记迁移和归档。

对应 AstrBot 连接插件：<https://github.com/zzz27578/astrbot-plugin-nest-diary-connector>

## 当前已实现

- Bot token API：`/api/v1/status`
- 日记写入：`/api/v1/diary/write`
- 日记读取：`/api/v1/diary/{date}`
- 日记搜索：`/api/v1/diary/search`
- 媒体归档：`/api/v1/media/attach`
- Markdown 日记落盘
- SQLite FTS5 + 中文 LIKE fallback 搜索
- 覆盖写入前 revision 快照
- SHA256 内容寻址媒体仓库
- 密码保护网页后台
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
NEST_ADMIN_PASSWORD=你的网页登录密码
NEST_BOT_API_TOKEN=一串很长的 bot token
TZ=Asia/Shanghai
```

启动：

```bash
docker compose up -d
```

默认端口是 `28080`。日记、媒体、索引和修订记录会保存在当前目录的 `data/` 中。

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

如果两个容器不在同一个 Docker 网络，可以改成宿主机或反代地址。

## 1Panel 本地应用支持

1Panel 本地应用包位于：

```text
deploy/1panel/nest-diary/
```

它使用镜像：

```text
ghcr.io/zzz27578/nest-diary-service:0.1.0
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

## 使用手册

见：

```text
docs/使用手册.md
```
