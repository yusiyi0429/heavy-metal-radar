# 重型演出雷达

微信小程序「重型演出雷达」— 自动监控秀动/大麦重型演出并推送企微通知。

## 快速启动

```bash
# 后端（端口 5001）
cd backend && pip install -r requirements.txt
python scripts/init_data.py        # 初始化种子数据
python -m backend.server            # 启动 API

# 定时调度器（独立进程）
python -m backend.scheduler

# 微信小程序
# 用微信开发者工具打开 miniprogram/ 目录，勾选"不校验合法域名"
```

## 架构

```
┌─────────────────────────────────────────────┐
│  微信小程序 (miniprogram/)                    │
│  pages/ ──▶ index / search / settings        │
│  utils/api.js ──▶ 后端 API                    │
└─────────────┬───────────────────────────────┘
              │ wx.request
              ▼
┌─────────────────────────────────────────────┐
│  Flask 后端 (backend/)                        │
│  server.py ──▶ API 路由 (7 个端点)            │
│  db.py ──▶ JSON 文件数据库 (线程安全)         │
│  scheduler.py ──▶ 定时抓取 + 企微通知         │
│  fetchers/ ──▶ 秀动(showstart) / 大麦(damai)  │
│  notifier/ ──▶ 企微机器人 Webhook 推送        │
└─────────────────────────────────────────────┘
```

## 目录结构

```
backend/
  server.py            # Flask API (7 个端点)
  db.py                # JSON 文件数据库 CRUD（线程安全）
  scheduler.py         # 定时抓取 + 企微通知（schedule 库）
  requirements.txt     # Python 依赖
  fetchers/
    __init__.py        # fetcher 注册
    base.py            # 基类：BaseFetcher
    showstart.py       # 秀动抓取器
    damai.py           # 大麦抓取器
    _nuxt_extract.js   # Nuxt 数据提取辅助脚本
  notifier/
    wecom_bot.py       # 企微机器人推送（Markdown 格式）
  data/
    config.json        # 配置（keywords/cities/enable_push/webhook_url）
    shows.json         # 演出数据
miniprogram/
  app.js               # 小程序入口，globalData.baseUrl
  app.json             # 页面路由、tabBar、导航配置
  app.wxss             # 全局样式
  pages/
    index/             # 首页：演出列表、城市筛选
    search/            # 搜索页：关键词搜索
    settings/          # 设置页：城市/关键词/推送开关
  components/
    show-card/         # 演出卡片组件（TDesign 风格）
  utils/
    api.js             # API 封装（超时/防抖/错误处理）
    constants.js       # 常量定义
  sitemap.json         # 小程序搜索索引
scripts/
  init_data.py         # 种子数据初始化
  test_api.py          # API 测试脚本
```

## 关键文件索引

| 文件 | 职责 | 修改风险 |
|------|------|----------|
| `backend/server.py` | Flask 路由总线，7 个 API 端点 | high（路由重复会静默覆盖） |
| `backend/db.py` | JSON 文件数据库，线程安全 Lock | high（并发写入会损坏数据） |
| `backend/scheduler.py` | 定时任务调度（抓取 + 通知） | medium |
| `backend/fetchers/showstart.py` | 秀动平台抓取器 | medium |
| `backend/fetchers/damai.py` | 大麦平台抓取器 | medium |
| `backend/notifier/wecom_bot.py` | 企微机器人推送 | low |
| `miniprogram/utils/api.js` | 前端 API 封装（基座 URL、超时、错误处理） | medium |
| `miniprogram/app.js` | 小程序入口，globalData.baseUrl 定义 | low |

## API 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/shows?city=&keyword=&status=&limit=&offset=` | 演出列表（支持分页、筛选） |
| GET | `/api/config` | 获取配置 |
| PUT | `/api/config` | 更新配置（keywords/cities/enable_push） |
| POST | `/api/fetch` | 触发抓取（秀动+大麦） |
| POST | `/api/notify` | 触发企微通知推送 |
| POST | `/api/reset` | 清除演出记录 |
| GET | `/api/health` | 健康检查 |

**⚠️ Flask 不检查重复路由** — 同名函数/路由会静默覆盖第二个定义。

## 天工 Agent 团队（9 人）

完整 prompt 见 `.claude/commands/*.md`，工作流编排见 `.claude/workflows/*.js`。

| 角色 | 职责 | 用法 |
|------|------|------|
| `/orchestrator` | 总调度：理解需求 → 委派角色 → 驱动修复回路 | `/orchestrator <高层需求>` |
| `/plan` | 规划师：需求分析 + 结构化实施计划 | `/plan <需求描述>` |
| `/dev` | **唯一编码者**：所有代码变更收口于此 | `/dev <需求>` |
| `/cr` | 审查员：diff 审查 + 安全审查 + 简化建议 | `/cr [--fix \|--comment]` |
| `/bug-hunt` | 缺陷猎人：全量代码扫描 | `/bug-hunt [scope]` |
| `/data-guardian` | 数据守护：JSON 数据结构 / 演出唯一键 / API 契约 | `/data-guardian <变更范围>` |
| `/test` | 测试工程师：生成并运行测试 | `/test <需求或范围>` |
| `/vr` | 运行验证官：启动后端 + 小程序路径验证 | `/vr <受影响的路径>` |
| `/ship-check` | 通关检查官：Python 语法 + 路由冲突 + 前后端同步 | `/ship-check` |

**data-guardian 触发条件**：
- `db.py` schema / JSON 数据结构变更
- API 端点请求/响应 JSON 结构变更
- `shows.json` / `config.json` 持久化格式变更
- 演出唯一键（`platform + showId`）变更
- 企微推送消息格式变更

**修复回路**: 所有问题统一交 `/dev` 落地修复。

## 关键约定

### 数据契约

| 约定 | 说明 |
|------|------|
| 演出唯一键 | `platform + showId`，入库前必须去重 |
| 演出状态 | `new` / `notified` / `expired` |
| 配置存储 | `backend/data/config.json`（gitignored，含 webhook_url） |
| 数据持久化 | JSON 文件，通过 `threading.Lock` 保证线程安全 |

### 抓取容错

- fetcher 抓取失败**必须返回空列表**，不抛异常，不阻塞主流程
- 秀动使用 requests 解析 HTML + Nuxt 数据提取
- 大麦使用 requests 解析 API 响应

### 安全约定

- **webhook_url** 在 `config.json` 中，已加入 `.gitignore`，**切勿 commit**
- 前端请求基座 URL 定义在 `app.js` `globalData.baseUrl`
- 本地开发 API 端口 **5001**，小程序 `urlCheck` 关闭

### 样式约定

- Brutalist 暗黑金属风格，TDesign 组件库
- 全局样式在 `app.wxss`，页面级在 `pages/*/index.wxss`
- 组件样式隔离：`components/show-card/*.wxss`

## 已知风险点

| 风险 | 严重度 | 说明 |
|------|--------|------|
| JSON 线程安全 | **critical** | `db.py` 读写必须通过 `threading.Lock`，防止并发写入损坏 |
| Webhook 密钥泄露 | **critical** | `config.json` 含 webhook_url，必须在 `.gitignore` 中 |
| 抓取失败阻断 | high | fetcher 抓取失败必须返回空列表，不抛异常 |
| 演出唯一键去重 | high | `platform + showId` 作为唯一键，入库前必须去重 |
| Flask 路由重复 | high | 同名函数/路由会静默覆盖 |
