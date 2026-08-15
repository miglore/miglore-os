# Miglore OS

个人成长操作系统。

## 目标

- 学习
- 求职
  - 投递方向
  - 投递记录
  - 面试记录
- 项目
- 任务
- 学习日志
- Blog

## 设计说明

首页设计参考 App Store 的信息组织方式（应用商店式卡片/网格/分类导航），但 UI 和业务逻辑由 Miglore OS 自己实现，不直接使用任何第三方前端源码。

## 项目结构

```
miglore-os-dev/
├── frontend/   # 前端（开发服务 127.0.0.1:5173）
├── backend/    # 后端 API
├── docs/       # 设计文档 / 架构文档
└── README.md
```

## 开发环境

- 开发服务绑定：`127.0.0.1:5173`（仅本机，不接公网域名）
- 与生产环境（/var/www/miglore.fun, miglore.service, Nginx, MySQL）完全隔离
