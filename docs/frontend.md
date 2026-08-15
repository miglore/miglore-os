# Miglore OS — 前端设计 (Svelte 5 + Vite + TypeScript)

> 本文件只做设计，**不写业务代码**。

## 1. 技术栈

| 项 | 选择 | 说明 |
|---|---|---|
| 框架 | Svelte 5 | runes（`$state`/`$derived`/`$effect`）响应式模型 |
| 构建 | Vite 6+ | dev 5173 / build 产物到 `dist/` |
| 语言 | TypeScript 5 | strict 模式 |
| 路由 | svelte-routing（Svelte 5 兼容版） | history 模式；若兼容性问题则退化为 hash 路由（部署最省事） |
| 样式 | 原生 CSS + CSS 变量（设计 token） | 不引 UI 框架，保持 App Store 式轻量与自控 |
| 状态 | 轻量 store（`$state` 模块级）+ fetch 封装 | 不引 Pinia/Redux，Svelte 5 runes 足够 |
| HTTP | fetch 封装（`apiFetch`） | 自动带 JWT、统一错误、401 刷新重试一次 |

## 2. 目录结构（规划）

```
frontend/
├── index.html
├── vite.config.ts
├── package.json
├── src/
│   ├── main.ts               # 入口：挂载 App + 路由 + 认证引导
│   ├── App.svelte            # 根组件：全局布局（顶栏 + 主区）
│   ├── routes/
│   │   ├── Home.svelte       # /
│   │   ├── Learning.svelte   # /learning
│   │   ├── Career.svelte     # /career
│   │   ├── Projects.svelte   # /projects
│   │   ├── Tasks.svelte      # /tasks
│   │   ├── Journal.svelte    # /journal
│   │   └── Blog.svelte       # /blog (V1 占位)
│   ├── components/
│   │   ├── layout/           # TopBar, SideNav, Footer
│   │   ├── home/             # Hero, ContinueLearning, LearningProgress,
│   │   │                     # FeaturedProjects, TodayTasks, RecentActivity, CareerStatus
│   │   ├── cards/            # TrackCard, ProjectCard, TaskItem, AppCard(通用卡片)
│   │   ├── shared/           # ProgressRing, Badge, Modal, EmptyState, Skeleton
│   │   └── forms/            # 通用表单字段
│   ├── lib/
│   │   ├── api.ts            # apiFetch + 端点常量
│   │   ├── auth.ts           # token 管理 / 登录态
│   │   ├── types.ts          # 全量 TS 类型（对应 database.md 各表）
│   │   └── format.ts         # 日期/时长/进度格式化
│   ├── stores/
│   │   └── dashboard.ts      # 首页聚合数据缓存（fetch-once）
│   └── styles/
│       ├── tokens.css        # 设计 token（色板/圆角/间距/阴影）
│       └── global.css        # 全局样式
```

## 3. 路由设计

| 路径 | 组件 | 说明 |
|---|---|---|
| `/` | Home | 聚合首页（dashboard） |
| `/learning` | Learning | 路线列表 + 详情（可 `/learning/:id`） |
| `/career` | Career | 方向看板 + 投递 + 面试（可 `/career/applications/:id`） |
| `/projects` | Projects | 项目网格 + 详情（可 `/projects/:id`） |
| `/tasks` | Tasks | 今日清单 + 全部任务（`?filter=`） |
| `/journal` | Journal | 学习日志时间线 |
| `/blog` | Blog | 模块入口（V1 占位） |

- 未登录：所有路由重定向到 `/login`（独立登录页，不入导航）
- 404 → 空状态页（App Store 风格空态插画文字）
- 部署：SPA history 路由 → Nginx `try_files $uri /index.html`（V2 部署时配）

## 4. 页面数据获取模式

```
route 挂载 → useDashboard() (stores/dashboard.ts)
  └─ 已有缓存? → 直接渲染 (Svelte 5 $state)
  └─ 无 → GET /api/dashboard → 写入 store → 渲染
```

- 每个页面一个 `load` 风格函数（无框架约定，纯函数 + `$effect` 触发）
- 写操作：乐观更新（先改本地 `$state`，请求失败回滚 + toast）
- 骨架屏：数据未到前显示 Skeleton 卡片（App Store 首屏体验）

## 5. 视觉设计原则（不复制 Apple UI，借鉴组织方式）

| 原则 | 落地 |
|---|---|
| 信息密度高 | 卡片网格 + shelf 横向滚动，一屏可扫全部模块 |
| 层级清晰 | Hero 大卡 → 次级 shelf → 网格卡片，视觉重量递减 |
| 数据可视化 | 进度环（ProgressRing）、技能条、streak 徽标 |
| 克制配色 | 单主色 + 中性灰阶，CSS 变量 token |
| 圆角 + 轻阴影 | 大圆角卡片（12-16px），hover 微浮起 |
| 暗色友好 | tokens.css 预留 `[data-theme="dark"]` 变量覆盖（V1 可不启用） |

## 6. 组件设计（关键组件）

| 组件 | 用途 | 备注 |
|---|---|---|
| `ProgressRing` | 路线/项目进度环 | SVG，可嵌套颜色 |
| `AppCard` | 通用内容卡片 | 标题 + 副标题 + 尾注（App Store 卡片式） |
| `Shelf` | 横向滚动分区容器 | 标题 + 箭头 + 横向列表 |
| `TaskItem` | 任务行 | 勾选框 + 标题 + 优先级/截止徽标，点击完成 |
| `Badge` | 状态徽标 | status → 颜色映射（tokens.css） |
| `TimelineItem` | 学习日志/活动条目 | 日期 + 内容 + 时长徽标 |
| `Modal` | 新建/编辑弹层 | 表单容器（不引组件库） |
| `Skeleton` | 加载骨架 | 首页分区加载态 |

## 7. 状态与类型

- `types.ts` 对齐 database.md 的 9 张表：`User, LearningTrack, Skill, Task, CareerDirection, JobApplication, Interview, Project, StudyLog` + 聚合 DTO：`DashboardData, CareerSummary`
- 枚举（TaskType/Status/Priority）用 TS union 类型，与 API 字符串对齐
- 认证态：`auth.ts` 持有 token + `$state` user；401 → 刷新 → 重试一次 → 失败跳登录
