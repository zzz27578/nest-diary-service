# 小窝日记服务

当前版本：`0.4.0`

仓库地址：<https://github.com/zzz27578/nest-diary-service>

这是小窝系统当前的 WebUI 与服务本体。它仍可独立部署，也会作为后续“插件内置 WebUI”的代码来源继续演进。

## 本轮架构调整

这版开始把小窝整理成模块化数据结构：

```text
data/
  system/
    settings/

  modules/
    diary/
      entries/YYYY/MM/YYYY-MM-DD.md
      index/nest.sqlite
      snapshots/YYYY/MM/YYYY-MM-DD/*.md
      drafts/

    impressions/
      people/*.json

    media/
      blobs/sha256/...
      by-date/YYYY/MM/YYYY-MM-DD/manifest.json

    archive/

  user_custom/
    webui/
      themes/
      modules/

  imports/
  logs/
```

设计原则：

- 官方代码和默认 WebUI 可以更新。
- 用户或 bot 自己改的前端放在 `user_custom/`，更新不覆盖。
- WebUI 设置里保留“外部 API Key”，只给 MCP、脚本、第三方网页等外部扩展使用。
- 插件内部调用小窝核心能力时不依赖 API Key。
- 日记模块可以在小窝设置里关闭；关闭后 WebUI 和 API 都不会执行日记写入/检索。

## 已实现功能

- 密码登录 WebUI，初始密码 `12345678`。
- 日记写入、编辑、删除。
- 年 / 月 / 日归档选择，只显示已有日记日期。
- 日记搜索，SQLite FTS5 + LIKE fallback。
- 图片 / 附件归档，媒体按 SHA256 存储。
- 人物印象管理。
- 设置页管理外部 API Key、日记模块开关、前端样式和自定义目录。
- ZIP 导入导出，优先备份 `system/`、`modules/`、`user_custom/`、`imports/`。
- 导入兼容旧目录：`diary/`、`memory/`、`media/`、`settings/`。
- 启动时会把旧目录缺失文件复制到新模块目录，不删除旧数据。
- 版本检测与可选 git 自更新。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:NEST_DATA_DIR = "data-dev"
$env:NEST_ADMIN_PASSWORD = "12345678"
uvicorn app.main:app --reload --host 127.0.0.1 --port 28080
```

打开：

```text
http://127.0.0.1:28080
```

## 外部 API

外部 API 默认建议关闭。需要给外部 MCP、脚本或第三方页面访问时：

1. 登录 WebUI。
2. 打开 `/settings`。
3. 在“访问密钥”里生成或填写外部 API Key。
4. 勾选“启用外部 API 访问”。

调用示例：

```bash
curl -H "Authorization: Bearer 你的外部APIKey" http://127.0.0.1:28080/api/v1/status
```

## 插件绑定

当前仍兼容独立服务模式。AstrBot 插件需要填写：

```text
service_url = http://nest-diary:28080
bot_api_token = WebUI 设置页里的外部 API Key
```

如果外部 API 没有启用，插件通过 HTTP 访问独立服务会被拒绝。后续合并为插件内置 WebUI 后，插件内部工具不需要 API Key。

## 自定义前端

默认自定义目录：

```text
data/user_custom/webui/
```

建议结构：

```text
themes/my-theme/
  theme.json
  templates/
  static/

modules/my-panel/
```

渲染策略应遵循：

```text
用户主题或模块存在 -> 使用用户版本
不存在 -> 回退官方默认 WebUI
```

更新前建议备份：

```text
data/user_custom/
```

## Docker / 1Panel

镜像：

```text
ghcr.io/zzz27578/nest-diary-service:0.4.0
```

1Panel 本地应用支持文件位于：

```text
deploy/1panel/nest-diary/
```

1Panel 只是可选部署方式；不用 1Panel 时，直接使用根目录 `docker-compose.yml` 即可。

## 静态 WebUI 预览

仓库根目录提供：

```text
webui-prototype.html
```

它可以直接打开，用来快速看设计效果。真实登录、写入、搜索、导入导出仍需启动服务。
