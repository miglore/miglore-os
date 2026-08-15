# Miglore OS — 架构设计

> 阶段：V1 架构设计（文档） | 状态：设计完成，待实现
> 技术栈：Svelte 5 + Vite + TypeScript / Flask REST API / MySQL / Nginx → Gunicorn → Flask

## 1. 设计目标

Miglore OS 是 miglore.fun 的核心应用。miglore.fun 打开后**直接进入 Miglore OS**，Blog 只是其中一个模块。

**V1 核心目标：**

> 每天打开 Miglore OS，我可以立即知道自己的职业目标、学习进度、今天应该做什么，以及最近做了什么。

首页视觉参考 Apple App Store 的信息组织方式（Hero → 分类 shelf → 卡片网格），**不复制 Apple UI**，整体感觉 = App Store 的信息密度 + 个人成长系统的数据感 + 个人操作系统的掌控感。

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│  Browser (桌面优先, 响应式)                              │
│  Svelte 5 SPA (Vite + TypeScript)                       │
│  路由: / /learning /career /projects /tasks /journal    │
│  /blog                                                  │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────┐
│  Nginx  (miglore.fun)                                   │
│  ├─ /api/*  →  proxy_pass 127.0.0.1:5000  (Flask API)  │
│  ├─ /static → 构建产物 alias, 缓存 30d                  │
│  └─ SPA fallback → index.html (history 路由)            │
└──────────────────────────┬──────────────────────────────┘
                           │ 127.0.0.1:5000
┌──────────────────────────▼──────────────────────────────┐
│  Gunicorn (Flask REST API, 无模板渲染)                  │
│  └─ 认证: JWT (Access + Refresh)                        │
└──────────────────────────┬──────────────────────────────┘
                           │ 127.0.0.1:3306
┌──────────────────────────▼──────────────────────────────┐
│  MySQL 8 (db: miglore_os)                               │
│  9 张表 (见 database.md)                                │
└─────────────────────────────────────────────────────────┘
```

### 分层职责

| 层 | 技术 | 职责 | 不做什么 |
|---|---|---|---|
| Frontend | Svelte 5 + Vite + TS | 渲染、路由、状态、API 调用、乐观更新 | 不直接访问 DB |
| API | Flask (REST) | 认证、校验、业务逻辑、聚合查询 | 不渲染 HTML 模板 |
| DB | MySQL 8 | 持久化 | — |
| 网关 | Nginx | TLS/静态资源/反代/SPA fallback | — |

### 关键决策

1. **前后端分离 SPA**：现有生产是 Jinja2 模板渲染；V1 改为纯 API + SPA，为后续多端（桌面/移动）留口。
2. **Blog 模块化**：V1 的 /blog 保留模块入口；内容迁移策略另行决定（现有 Hexo/gh-pages 产物或新 CMS），V1 先做占位 + 外链跳转，不阻塞主应用。
3. **单库单应用**：db `miglore_os` 独立于生产 `miglore` 库，开发/生产各自实例，物理隔离。
4. **JWT 认证**：API 无状态，前端存储 token（httpOnly cookie 或 localStorage——实现阶段定夺）。
5. **聚合接口**：首页一个 `GET /api/dashboard` 一次拉取全页数据，避免 N+1 请求（App Store 式首屏速度）。

## 3. 信息架构 (IA)

```
Miglore OS
├── Home      /         个人操作系统首页（聚合视图）
├── Learning  /learning 学习路线 + 技能 + 学习任务
├── Career    /career   求职：投递方向 / 投递记录 / 面试记录
├── Projects  /projects 项目 + 项目任务
├── Tasks     /tasks    今日任务 / 待办清单
├── Journal   /journal  学习日志（时间线）
└── Blog      /blog     博客（模块占位）
```

### 模块与页面

| 模块 | 页面/视图 | 核心数据 | 对应 API |
|---|---|---|---|
| Home | 1 页聚合 | 路线进度、继续学习、今日任务、最近活动、求职状态 | /api/dashboard |
| Learning | 路线列表、路线详情（技能+任务）、技能清单 | tracks/skills/tasks | /api/learning, /api/skills, /api/tasks |
| Career | 方向看板、投递列表+详情、面试时间线 | directions/applications/interviews | /api/career, /api/applications, /api/interviews |
| Projects | 项目网格、项目详情（任务+日志） | projects/tasks/study_logs | /api/projects, /api/tasks |
| Tasks | 今日清单、全部任务（按状态/日期过滤） | tasks | /api/tasks |
| Journal | 学习日志时间线、按日期聚合 | study_logs | /api/journal |
| Blog | 模块入口（V1 占位） | — | — |

### Career 边界（明确不做）

Career **只包含** 投递方向 / 投递记录 / 面试记录。不做：简历生成、招聘系统、人才库、offer 管理流程、薪资对比。

## 4. 模块关系

```
users ──┬── learning_tracks ──┬── skills
        │                     └── tasks(学习类)
        ├── projects ──────────── tasks(项目类)
        ├── tasks(日常)
        ├── study_logs
        ├── career_directions ── job_applications ── interviews
        └── (Blog: V1 占位)
```

详见 database.md 的 ER 图与字段定义。

## 5. 非功能约束

- 首屏数据：单次 dashboard 聚合请求，P95 < 300ms（本机）
- 认证：JWT Access(15min) + Refresh(7d)，密码 bcrypt
- 数据隔离：所有查询强制 `user_id` 过滤（多租户单用户语义，为未来开放注册预留）
- API 统一响应：`{data}` 成功 / `{error:{code,message}}` 失败
- 开发环境：127.0.0.1:5173 (Vite) + 127.0.0.1:5001 (Flask dev, 与生产 5000 错开) —— 实现阶段确认端口

## 6. 开发/生产环境隔离

| 项 | 开发 | 生产 |
|---|---|---|
| 目录 | /home/ubuntu/miglore-os-dev | /var/www/miglore.fun (V2 迁移) |
| DB | dev MySQL 实例 (miglore_os) | 生产 miglore (不动) |
| 域名 | 无，127.0.0.1 | miglore.fun |
| 端口 | 5173 (Vite), 5001 (Flask) | 5000 (Gunicorn) |

> V1 开发期间生产 miglore.fun 保持现状运行，**不受影响**。
