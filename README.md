# Miglore OS

个人成长操作系统。

> 每天打开 Miglore OS，我可以立即知道自己的职业目标、学习进度、今天应该做什么，以及最近做了什么。

## 项目目标

- 学习
- 求职（投递方向 / 投递记录 / 面试记录）
- 项目
- 任务
- 学习日志
- Blog

首页设计参考 App Store 的信息组织方式（Hero → shelf → 卡片网格），UI 与业务逻辑全部由 Miglore OS 自己实现，不复制任何第三方前端源码。

## 技术栈

| 层 | 技术 |
|---|---|
| Frontend | Svelte 5 + Vite + TypeScript |
| Backend | Flask (REST API) |
| Database | MySQL |
| Deployment | Nginx → Gunicorn → Flask |

## 当前阶段

**V1 架构设计阶段（进行中）**——已完成：
- [x] 项目初始化（目录骨架 + Git）
- [x] 架构设计（architecture / database / api / frontend / home-wireframe）
- [ ] 数据模型实现（Alembic 迁移 + dev 库）
- [ ] 后端 REST API
- [ ] 前端 Svelte 5 SPA
- [ ] 本地联调（127.0.0.1:5173）
- [ ] 上线迁移（替换 miglore.fun 生产，需用户确认）

## 文档索引

| 文档 | 内容 |
|---|---|
| [docs/architecture.md](docs/architecture.md) | 总体架构、模块划分、开发/生产隔离 |
| [docs/database.md](docs/database.md) | ER 模型、9 张表设计、索引、简化决策 |
| [docs/api.md](docs/api.md) | REST API 契约（认证 + 聚合 + 资源接口） |
| [docs/frontend.md](docs/frontend.md) | 前端目录结构、路由、组件、视觉原则 |
| [docs/home-wireframe.md](docs/home-wireframe.md) | 首页线框设计（App Store 式信息组织） |

## 项目结构

```
miglore-os-dev/
├── frontend/   # 前端（开发服务 127.0.0.1:5173，未启动）
├── backend/    # 后端 API（未创建）
├── docs/       # 设计文档（已完成 V1 架构设计）
└── README.md
```

## 开发环境

- 开发服务绑定：`127.0.0.1:5173`（仅本机，不接公网域名）
- 与生产环境（/var/www/miglore.fun, miglore.service, Nginx, MySQL `miglore` 库）**完全隔离**
- V1 开发期间生产 miglore.fun 保持现状运行，不受影响
