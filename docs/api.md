# Miglore OS — REST API 设计

> 本文件只设计 API 契约，**不实现**。前缀 `/api`，统一 JSON。

## 1. 通用约定

| 项 | 约定 |
|---|---|
| Base URL | `/api` |
| 认证 | Bearer JWT：`Authorization: Bearer <access_token>`（15min）+ Refresh（7d） |
| 内容类型 | `application/json; charset=utf-8` |
| 成功响应 | `{"data": ...}` |
| 错误响应 | `{"error": {"code": "NOT_FOUND", "message": "..."}}`，HTTP 4xx/5xx |
| 分页 | `?page=1&per_page=20` → `{"data": [...], "meta": {"page":1,"per_page":20,"total":N}}` |
| 过滤 | 按字段 `?status=active&from=2026-08-01&to=2026-08-31` |
| 排序 | `?sort=-created_at`（`-` 表示倒序） |
| 数据隔离 | 所有查询强制按当前用户 `user_id` 过滤，**永不越权** |

### 错误码

| code | 含义 |
|---|---|
| UNAUTHORIZED | 未登录/token 失效 (401) |
| FORBIDDEN | 无权限 (403) |
| NOT_FOUND | 资源不存在 (404) |
| VALIDATION_ERROR | 参数校验失败 (422)，message 含字段明细 |
| CONFLICT | 冲突（如重复用户名）(409) |
| RATE_LIMITED | 限流 (429) |

## 2. 认证接口

| Method | Path | 说明 |
|---|---|---|
| POST | /api/auth/register | 注册 `{username, email, password}` → 返回 token + user |
| POST | /api/auth/login | 登录 `{username, password}` → `{access_token, refresh_token, user}` |
| POST | /api/auth/refresh | 刷新 token `{refresh_token}` |
| POST | /api/auth/logout | 注销（吊销 refresh） |
| GET | /api/auth/me | 当前用户信息（含 career_goal） |
| PATCH | /api/auth/me | 更新 profile（display_name, avatar_url, career_goal） |

## 3. 首页聚合（核心接口）

### GET /api/dashboard — 首页一次性聚合

一次请求返回首页全部数据（App Store 式首屏，避免 N 次请求）。

```json
{
  "data": {
    "hero": {
      "career_goal": "DevOps 工程师",
      "today": "2026-08-15",
      "streak_days": 12,
      "active_track": {"id": 1, "title": "DevOps 学习计划", "progress": 68}
    },
    "continue_learning": [
      {"id": 10, "type": "learning", "title": "Docker Compose 编排实战",
       "track_id": 1, "track": "DevOps 学习计划", "due_date": "2026-08-16", "status": "in_progress"}
    ],
    "learning_progress": [
      {"id": 1, "name": "Nginx", "level": 4, "target_level": 5, "status": "learning"},
      {"id": 2, "name": "Docker", "level": 4, "target_level": 5, "status": "learning"}
    ],
    "featured_projects": [
      {"id": 3, "name": "Miglore OS", "tech_stack": "Svelte,Flask,MySQL",
       "status": "active", "progress": 15, "featured": 1}
    ],
    "today_tasks": [
      {"id": 21, "title": "完成 API 设计文档", "type": "project", "priority": 3,
       "status": "todo", "due_date": "2026-08-15", "project": "Miglore OS"}
    ],
    "recent_activity": [
      {"id": 99, "log_date": "2026-08-14", "content": "完成 MySQL 主从原理…",
       "duration_min": 90, "mood": 4}
    ],
    "career_status": {
      "active_directions": 1,
      "applications_total": 8,
      "applications_interviewing": 2,
      "interviews_pending": 1,
      "offers": 0
    }
  }
}
```

## 4. 资源接口

### 4.1 Learning / Skills / Tasks

| Method | Path | 说明 |
|---|---|---|
| GET | /api/learning | 学习路线列表（含技能数与进行中任务数） |
| POST | /api/learning | 新建路线 |
| GET | /api/learning/{id} | 路线详情：基本信息 + skills + 学习任务 |
| PATCH | /api/learning/{id} | 更新路线（含 progress/status） |
| DELETE | /api/learning/{id} | 删除路线（软删） |
| GET | /api/skills | 技能列表（`?track_id=&status=`） |
| POST | /api/skills | 新增技能 |
| PATCH | /api/skills/{id} | 更新（level/status） |
| DELETE | /api/skills/{id} | 删除 |
| GET | /api/tasks | 任务列表（`?type=&status=&due=2026-08-15&project_id=&track_id=`） |
| POST | /api/tasks | 新建任务（type 决定可带的外键） |
| GET | /api/tasks/{id} | 任务详情 |
| PATCH | /api/tasks/{id} | 更新（status/priority/due_date…） |
| DELETE | /api/tasks/{id} | 删除（软删） |
| PATCH | /api/tasks/{id}/complete | 快捷完成（置 done + completed_at） |

### 4.2 Career

| Method | Path | 说明 |
|---|---|---|
| GET | /api/career | 求职汇总：方向列表 + 每个方向的投递数/状态计数 + 总览统计 |
| POST | /api/career/directions | 新建投递方向 |
| PATCH | /api/career/directions/{id} | 更新方向 |
| DELETE | /api/career/directions/{id} | 删除（级联软删其投递） |
| GET | /api/applications | 投递列表（`?direction_id=&status=&from=&to=`） |
| POST | /api/applications | 新建投递 |
| GET | /api/applications/{id} | 投递详情（含 interviews 时间线） |
| PATCH | /api/applications/{id} | 更新（状态流转：applied→interviewing→offer/rejected） |
| DELETE | /api/applications/{id} | 删除（级联软删面试） |
| GET | /api/interviews | 面试列表（`?application_id=&result=&from=&to=`，可含今日/待面试） |
| POST | /api/interviews | 新建面试（挂 application_id） |
| PATCH | /api/interviews/{id} | 更新（结果/复盘 review） |
| DELETE | /api/interviews/{id} | 删除 |

### 4.3 Projects

| Method | Path | 说明 |
|---|---|---|
| GET | /api/projects | 项目列表（`?status=&featured=1`） |
| POST | /api/projects | 新建项目 |
| GET | /api/projects/{id} | 项目详情：信息 + project 类任务 + 关联学习日志 |
| PATCH | /api/projects/{id} | 更新（status/progress/featured） |
| DELETE | /api/projects/{id} | 删除（软删） |

### 4.4 Journal

| Method | Path | 说明 |
|---|---|---|
| GET | /api/journal | 学习日志时间线（`?from=&to=&track_id=&project_id=`，按 log_date 倒序） |
| GET | /api/journal/{date} | 某日日志详情（y/m-d 或 ISO 日期） |
| POST | /api/journal | 新建日志 `{log_date, content, duration_min, mood, track_id?, project_id?}` |
| PATCH | /api/journal/{id} | 更新日志 |
| DELETE | /api/journal/{id} | 删除 |

## 5. API 设计要点

1. **REST 语义**：资源名词 + HTTP 动词；`/api/career` 是聚合视图（dashboard 的缩小版），方向/投递/面试是独立资源。
2. **聚合接口只读**：dashboard/career/learning 聚合 GET 只读；写操作一律走具体资源接口。
3. **乐观更新支持**：前端先渲染后请求，API 返回 409/422 时回滚。
4. **无嵌套过深**：最多两级（`/applications/{id}/interviews` 不单独提供，详情里内嵌即可）。
5. **版本**：V1 不做 `/v1` 前缀（单版本）；破坏性变更时再加。
6. **SQL 层面**：聚合接口用 2-4 条索引查询拼装（dashboard ≈ 7 组查询，全部命中 user_id 索引），不做 N+1。
