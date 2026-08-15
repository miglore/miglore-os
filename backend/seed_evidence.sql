-- Miglore OS 真实项目证据 (project_id=1, 全部基于实际完成的工作)
-- 注入 compose 容器 mysql (仅开发环境)

USE miglore_os;

-- ========== Technical Evidence (10 条) ==========
INSERT INTO project_evidence (user_id, project_id, title, category, description, technical_detail, result) VALUES
(1, 1, 'Docker 容器化 (multi-stage + 非 root)', 'docker',
 '将 Flask 后端与 Svelte 前端容器化，前端采用 multi-stage 构建。',
 'backend: python:3.12-slim + gunicorn 非 root appuser，预建 /generated-posts 并 chown；frontend: node:22-alpine 构建 → nginx:alpine 托管 dist，SPA fallback + /api 反代到 backend 服务名。',
 '镜像构建成功，容器内以非 root 运行，写 volume 权限正常'),

(1, 1, 'Docker Compose 编排 (5 服务)', 'docker',
 'backend/frontend/mysql/prometheus/grafana 五服务 compose 编排。',
 '所有宿主端口仅绑定 127.0.0.1；mysql 独立 volume 且无宿主端口映射（仅容器网络）；依赖健康检查排序（mysql healthy → backend）；MySQL initdb 自动执行 schema+seed；踩坑：挂载 SQL 600 权限导致 entrypoint Permission denied，chmod 644 修复。',
 '5 容器全部 healthy，生产 3306/5000 完全隔离'),

(1, 1, 'GitHub Actions CI 流水线', 'ci_cd',
 '三 job CI：backend pytest（mysql service）+ frontend check/build + docker 双镜像构建。',
 '.github/workflows/ci.yml：backend job 用 services.mysql 独立测试库 miglore_os_test；frontend job npm ci + svelte-check + vite build；docker job 串行构建 backend/frontend 镜像。',
 'CI GREEN，每次 push 自动验证 40+ 后端测试与前端构建'),

(1, 1, 'Prometheus 监控接入', 'monitoring',
 'Prometheus 抓取 backend /metrics 与自身指标。',
 'prometheus.yml 静态配置两个 job（prometheus、backend:5001）；backend 通过 prometheus-client 暴露 http_requests_total Counter 与 latency Histogram。',
 '故障实验验证：stop backend → up=0 DOWN，start → 恢复 UP=1'),

(1, 1, 'Grafana 可视化 (provisioning)', 'monitoring',
 'Grafana 自动注册 Prometheus 数据源并加载 Miglore OS Overview 仪表盘。',
 '声明式 provisioning（datasources.yml + dashboards provider）；仪表盘 5 面板：request rate / p95 latency / 5xx error rate / uptime / target status；grafana.ini 环境变量配置开发专用账号。',
 'Grafana→Prometheus 查询链路实测 up 返回 backend=1/prometheus=1'),

(1, 1, 'Flask 应用指标 (prometheus-client)', 'monitoring',
 '给 Flask API 增加基础 Prometheus 指标与 /metrics 端点。',
 'before/after_request 钩子：http_requests_total{method,path,status} Counter + http_request_duration_seconds Histogram；path 用 Flask url_rule 模板避免高基数。',
 '压测验证：60 次 /api/health 后 request rate 0.055→0.198 req/s（3.6x 增长，指标真实）'),

(1, 1, 'systemd 服务单元与守护关系', 'linux',
 '生产 miglore.service 结构与 systemd 对 Gunicorn MainPID 的守护。',
 '生产 systemd 单元：WorkingDirectory=/var/www/miglore.fun，ExecStart gunicorn --workers 2 --bind 127.0.0.1:5000，Restart=always + RestartSec=5，User=ubuntu；对比 Docker restart policy（unless-stopped 尊重手动 stop、always 会拉起）。',
 '服务自 6 月起连续运行未中断，系统重启可自动拉起'),

(1, 1, 'Nginx 反向代理与 SPA 部署', 'architecture',
 'Nginx 承载生产站点与开发容器前端。',
 '生产：/static alias 缓存 30d + 动态 / proxy_pass 5000 + gzip；容器前端：nginx.conf SPA try_files fallback + /api/ proxy_pass backend:5001 + 静态资源 immutable 缓存。',
 '本地直连 127.0.0.1:80 HTTP 200，SPA 路由与 API 代理正常'),

(1, 1, '容器权限故障排查 (Linux)', 'troubleshooting',
 '排查 docker-entrypoint-initdb.d 与 provisioning 文件权限导致的容器启动失败。',
 '症状：mysql initdb Permission denied、prometheus config permission denied、grafana provisioning 读取失败；用 ls -la 定位文件 600 权限，容器内进程（mysql/nobody/appuser）无法读取；修复：文件 644 + 目录 755，重建容器验证。',
 '同类问题一次定位，容器全部恢复 healthy'),

(1, 1, 'CI 首次失败分析与修复', 'ci_cd',
 'CI 首轮失败根因定位：npm lockfile 锁定腾讯内网镜像，GitHub 海外 runner 无法拉包。',
 '排查：本地全流程通过但 CI 失败 → 检查 package-lock.json 发现 74 个 resolved 指向 http://mirrors.tencentyun.com/npm/；修复：重建 lockfile + frontend/.npmrc 固定 registry.npmmirror.com（公网可达）；本地模拟 npm ci 全流程验证后重推。',
 'CI 第二轮 GREEN，未删除/降低任何测试');

-- ========== Milestones (Stage 1-6) ==========
INSERT INTO project_milestones (user_id, project_id, title, status, sort_order, achieved_at) VALUES
(1, 1, 'Stage 1 · Architecture',    'done',    1, '2026-08-15'),
(1, 1, 'Stage 2 · Learning',        'done',    2, '2026-08-15'),
(1, 1, 'Stage 3 · Study Logs',      'done',    3, '2026-08-15'),
(1, 1, 'Stage 4 · Docker + Testing + CI', 'done', 4, '2026-08-15'),
(1, 1, 'Stage 5 · Prometheus + Grafana', 'done', 5, '2026-08-15'),
(1, 1, 'Stage 6 · Career + JD Analyzer', 'current', 6, NULL);

-- ========== Interview Evidence (2 条, 关联现有 skills) ==========
INSERT INTO interview_evidence (user_id, project_id, evidence_id, skill_id, question, answer) VALUES
(1, 1, 1, 5, '你 Docker 用到什么程度？',
 '基于 Miglore OS 实际部署：前端 multi-stage 构建（node 构建层 → nginx 运行层，镜像只保留 dist 产物），后端 python slim 镜像以非 root 用户运行；Docker Compose 编排 5 个服务，MySQL 用独立 volume 持久化、无宿主端口映射；每个服务配了 healthcheck，mysql 用 mysqladmin ping 做依赖就绪排序。'),
(1, 1, 3, 6, 'CI/CD 怎么保证代码质量？',
 'GitHub Actions 三 job 流水线：backend 用 services.mysql 起独立测试库跑 40+ pytest 用例，frontend 跑 svelte-check 类型检查 + vite build，最后 docker build 验证镜像可构建。遇到过一次真实失败：lockfile 锁了内网镜像源导致海外 runner 拉不到包，通过重建 lockfile 改用公网 npmmirror 修复，没有绕过测试。');

-- 更新项目进度 (证据就绪)
UPDATE projects SET progress = 20, tech_stack = 'Svelte 5 · Flask · MySQL · Docker · Prometheus · Grafana' WHERE id = 1;
