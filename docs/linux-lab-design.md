# Miglore OS — Linux Engineer Roadmap V2 + Linux Lab 设计

> 状态: 设计稿 (V1 最小可行版) | 日期: 2026-08-16 | 未实施, 等待确认
> 职业目标: **Linux 工程师** (替代原 DevOps 主路线)

## 0. 现状盘点 (只读, 已完成)

| 维度 | 现状 |
|---|---|
| 认证 | 单用户 USER_ID=1 固定 (JWT/登录 V1.1 后置), 无 session 体系 |
| 后端 API | 32 个路由 (learning/dashboard/tasks CRUD/study-logs/career/projects/evidence/jd-analyze/metrics), **无 lab/terminal 相关** |
| tasks 表 | type(learning/project/daily) + status + track_id + skill_id + sort_order + completed_at —— **可承载 Lab 任务** |
| learning_tracks | title/status(active)/progress/sort_order —— 可新增 "Linux Engineer Roadmap V2" (sort_order=2) |
| skills | 8 项 (Linux learned 4级/计算机网络/systemd/Nginx/Docker...), 可直接复用 |
| frontend | hash 路由 (App.svelte), api.ts fetch 封装 (API_BASE=''), Svelte 5 + tokens |
| compose | backend:5001 / frontend:5173 / mysql / prometheus:9090 / grafana:3000, 全部 127.0.0.1 |
| Docker 网络 | miglore-os_default bridge 172.20.0.0/16 (5 容器), 无宿主机端口暴露的生产服务 |
| 数据 | 1 track (Linux → DevOps, 50%) / 10 tasks / 8 skills —— **保持不动, 新增第二 track** |

## 1. Linux Lab 架构设计

```
Browser (Lab.svelte Web Terminal UI)
    │  fetch (V1)  /  WebSocket (V2 预留)
    ▼
frontend (nginx :5173, /api 反代)
    ▼
backend (Flask :5001, 新增 /api/lab/*)
    │  docker SDK / CLI (挂载 /var/run/docker.sock, 仅操作 miglore-os-lab-* 容器)
    ▼
Docker Engine (宿主)
    └─▶ lab 容器 (ubuntu:24.04, 独立网络 miglore-os_lab, 无端口映射)
```

- **V1 = REST 一次性命令模式** (`docker exec` 无 TTY): ls/cd/cat/grep/管道/重定向/文件操作 全覆盖
- **V2 = PTY + WebSocket**: `docker exec -it` + 伪终端流 (见 §4)
- Lab 容器由 backend 按需创建/Reset (docker.sock), 与生产栈不同网络

## 2. Docker 隔离方案

| 维度 | 配置 | 说明 |
|---|---|---|
| 镜像 | `ubuntu:24.04` (官方, 含 apt) | 可安装软件包 (实验需要) |
| 特权 | **非 privileged** | 禁止逃逸 |
| 能力 | `--cap-drop ALL --cap-add CHOWN,DAC_OVERRIDE,FOWNER,SETUID,SETGID,SETGID` | 支撑 chmod/chown/useradd 实验 |
| 资源 | `--memory 512m --cpus 0.5 --pids-limit 256` | 防 fork 炸弹/资源耗尽 |
| 挂载 | **零宿主目录挂载** | 不暴露 /proc /sys /rootfs (用户明确禁止) |
| 网络 | 独立 `miglore-os_lab` bridge | 不加入 miglore-os_default, 无法访问生产服务 |
| 端口 | **无端口映射** | 仅经 backend docker exec 交互 |
| 重置 | `docker rm -f` + recreate | 一键还原 |

## 3. Web Terminal 实现方案 (V1)

- **后端**: `POST /api/lab/exec {cmd}` → `docker exec <lab> sh -c cmd` (timeout 10s) → 返回 `{stdout, stderr, exit_code}`
- **前端**: Lab.svelte — `<pre>` 输出区 + 命令输入框 + 历史 (↑↓) + 常用命令按钮; App Store 风格卡片
- **限制 (V1 明示)**: 不支持全屏交互程序 (vim/top/htop 需 TTY, V2 引入), 每次执行一次性命令
- 工作目录跨请求保持: 使用 `cd <dir> && <cmd>` 会话包装 (会话目录存 backend 内存/Redis 后置)

## 4. PTY / WebSocket 方案 (V2 预留)

- **V2 架构**: backend 加 `websockets`/`Flask-SocketIO`; `GET /ws/lab` 建立双工通道
- 后端用 Python `pty` + subprocess 创建 PTY (`docker exec -it` 经 unix socket 交互) → 读 PTY 输出 → WS 推送; 前端引入 `xterm.js`
- **V1 不实现 PTY/WS**, 但 API 路径 `/ws/lab` 与 exec 响应结构已按双工可扩展设计 (exec 返回可演进为流式帧)

## 5. 安全边界

1. **Lab 容器不可达生产**: 独立网络 + 无端口 + 非特权 + cap-drop → 无法访问 127.0.0.1 宿主端口与生产服务
2. **无宿主文件暴露**: 零挂载 → 容器内 rm -rf / 只影响自身 (可 Reset 兜底)
3. **命令自由但可重置**: V1 允许全命令 (学习需要 rm/chmod/useradd), 依赖隔离+Reset 兜底; **全部命令落日志** (lab_sessions 或文件)
4. **backend 的 docker.sock 权限**: 只操作名称前缀 `miglore-os-lab-*` 的容器 (create/inspect/exec/rm), 其余操作拒绝; 开发环境可接受, **V2 抽独立 lab-manager 服务** (backend 仅 HTTP 调用, 不持 socket)
5. **资源防滥用**: memory/cpu/pids 限制 + exec timeout
6. **生产零接触**: 不修改现有 compose 服务/网络/数据库结构; 仅新增 lab 服务与网络

## 6. Task 与 Lab 的关系

- 新 track: `learning_tracks` 插入 `Linux Engineer Roadmap V2` (active, sort_order=2)
- **L0 首批 15 任务** (仅此阶段): 01 认识 Linux / 02 pwd / 03 ls / 04 cd / 05 mkdir / 06 touch / 07 cp / 08 mv / 09 rm / 10 cat / 11 less / 12 head-tail / 13 grep / 14 find / 15 综合文件操作实验
- 任务表: 复用 `tasks` (type='learning', track_id=新track, sort_order=1-15, skill_id→Linux)
- Lab 页 = 任务列表 + 终端: 每任务描述含实验目标, 用户在终端实操后点「验证」

## 7. 实验验证机制

- `POST /api/lab/verify {task_id}` → backend 执行**预定义验证脚本** (V1 硬编码 dict: task_id → shell 验证命令)
  - 例: task 05 mkdir → `test -d /tmp/miglab && echo PASS`
  - 例: task 15 综合实验 → 多步断言脚本
- PASS → 后端调用现有 `PATCH /api/tasks/<id>` 逻辑置 done (复用) + 返回反馈; FAIL → 返回 hint
- 验证脚本与 L0 任务一一对应, 数据驱动 (V2 落库 lab_verifications 表)

## 8. 数据库是否需要修改

**V1 结论: 零结构修改 (ALTER-free)**
- 复用: `tasks` / `learning_tracks` / `skills` 现有字段完全够用
- 仅需**插入数据** (seed): 1 条新 track + 15 条 L0 任务 (与既有数据并行, 不删不改)
- V2 可选新增表: `lab_verifications` (验证脚本), `lab_sessions` (命令历史) —— V1 用 backend 硬编码 dict + 日志文件替代

## 9. 可复用现有系统

- ✅ tasks/learning_tracks/skills 表与 PATCH /api/tasks 完成逻辑
- ✅ frontend: api.ts fetch 封装 / tokens.css / Badge/Shelf/卡片组件 / hash 路由
- ✅ compose 网络模式 (新增独立 lab 网络), Docker 实验环境本身
- ✅ Prometheus: lab 容器后期可加指标 (V1 不需要)
- ✅ docs/ 设计文档流程, CI/pytest 基建
- 改造点: backend 新增 lab 模块 (独立文件, 不侵入现有路由); frontend 新增 Lab.svelte + 路由

## 10. V1 最小可行版本 (范围清单)

| 项 | 内容 |
|---|---|
| 后端 | `POST /api/lab/exec` / `POST /api/lab/reset` / `POST /api/lab/verify` (3 端点, lab.py 独立模块) |
| 容器 | `miglore-os-lab` (ubuntu:24.04, 非特权, 独立网络 miglore-os_lab, 无端口, 512m/0.5cpu/pids 限制) |
| 数据 | seed: "Linux Engineer Roadmap V2" track + 15 个 L0 任务 (插入, 不动现有) |
| 前端 | `#/lab` 路由 + Lab.svelte (终端 UI + L0 任务列表 + 验证按钮 + 空态/加载/错误) |
| 验证 | 15 条验证脚本 (硬编码 dict), PASS→任务 done (复用 PATCH) |
| 不做 | PTY/WebSocket (V2)、多用户、JWT、其他 L1-L15 阶段、lab 指标 |

**风险说明**: backend 挂载 docker.sock 是唯一敏感点 (开发环境可接受, 仅 127.0.0.1); V2 迁移为独立 lab-manager 服务。
