# 小窝日记服务

这是小窝日记系统的本体服务。

它独立于 AstrBot 运行，负责网站、API、日记存储、媒体存储、搜索索引、版本追溯、旧日记迁移和归档。

## 第一版目标

- 提供 bot 专属 API。
- 提供密码保护的私密网页后台。
- 用 Markdown 保存日记正文。
- 用 SQLite FTS5 做全文搜索。
- 用 SHA256 内容寻址保存图片、语音和附件。
- 支持普通 Docker Compose 部署。
- 可选提供 1Panel 本地应用包。

## 运行方式

复制 `.env.example` 为 `.env`，修改密码和 token 后启动：

```bash
docker compose up -d
```

默认端口是 `28080`。日记、媒体、索引和修订记录会保存在当前目录的 `data/` 中。

## AstrBot 连接

在 AstrBot 连接插件中配置：

```text
service_url = http://nest-diary:28080
bot_api_token = 与 NEST_BOT_API_TOKEN 相同
```

如果两个容器不在同一个 Docker 网络，可以改成宿主机或反代地址。

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
