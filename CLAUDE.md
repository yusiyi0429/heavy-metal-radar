# CLAUDE.md — Heavy Metal Radar

微信小程序「重型演出雷达」— 个人工具，自动监控秀动/大麦重型演出并推送企微通知。

## 架构

```
Flask 本地 Mock 后端 (backend/)  ──API──▶  微信原生小程序 (miniprogram/)
                 │
                 └──▶ 企微机器人 Webhook (通知推送)
```

## 技术栈

- **后端**: Flask 3.x + requests + schedule（本地 Mock，后续迁微信云开发 CloudBase）
- **前端**: 微信原生小程序框架（Vanilla JS + WXSS）
- **数据**: JSON 文件持久化（backend/data/），模拟云数据库
- **推送**: 企业微信机器人 Webhook（Markdown 格式消息）

## 项目结构

```
backend/
  server.py          # Flask API (7 endpoints)
  db.py              # JSON 文件数据库 CRUD（线程安全）
  scheduler.py       # 定时抓取+通知（schedule 库）
  fetchers/          # 平台抓取器（秀动/大麦）
  notifier/          # 企微机器人推送
  data/              # 数据文件 (gitignore: config.json 含 webhook 密钥)
miniprogram/
  pages/             # 首页(index) / 搜索(search) / 设置(settings)
  components/        # show-card 演出卡片组件
  utils/             # api.js (API 封装) / constants.js
scripts/
  init_data.py       # 种子数据初始化
```

## API 契约

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/shows?city=&keyword=&status=&limit=&offset= | 演出列表 |
| GET | /api/config | 获取配置 |
| PUT | /api/config | 更新配置 (keywords/cities/enable_push) |
| POST | /api/fetch | 触发抓取 |
| POST | /api/notify | 触发通知推送 |
| POST | /api/reset | 清除演出记录 |
| GET | /api/health | 健康检查 |

## 启动方式

```bash
# 后端
cd backend && pip install -r requirements.txt
python scripts/init_data.py    # 初始化种子数据
python -m backend.server        # 启动 API (127.0.0.1:5001)

# 定时调度器（独立进程）
python -m backend.scheduler

# 小程序
# 用微信开发者工具打开 miniprogram/ 目录，勾选"不校验合法域名"
```

## 关键约定

- 演出唯一键：platform + showId
- 抓取失败返回空列表，不抛异常，不阻塞主流程
- 企微 Webhook URL 在 config.json 中，gitignore 防止泄露
- 本地开发 API 端口 5001，小程序 urlCheck 关闭
- 前端请求基座 URL 定义在 app.js globalData.baseUrl
