-- Miglore OS V1 — 初始测试数据 (仅 miglore_os 开发库)
-- 学习路线: Linux → DevOps (8 阶段)
-- 不涉及生产数据库

-- 1. 用户 (单用户系统, id=1)
INSERT INTO users (id, username, email, password_hash, display_name, career_goal)
VALUES (1, 'miglore', 'miglore@miglore.fun', 'seed-only-no-login', 'miglore', 'DevOps 工程师');

-- 2. 学习路线
INSERT INTO learning_tracks (id, user_id, title, description, status, progress, started_at, sort_order)
VALUES (
  1, 1, 'Linux → DevOps',
  'DevOps 工程师成长路线，共 8 阶段：\n1. Linux 基础\n2. 网络基础\n3. systemd\n4. Nginx\n5. Docker\n6. CI/CD\n7. Monitoring\n8. Kubernetes',
  'active', 50, '2026-06-01', 1
);

-- 3. 技能 (对应 8 阶段)
INSERT INTO skills (user_id, track_id, name, level, target_level, status) VALUES
(1, 1, 'Linux',        4, 5, 'learning'),
(1, 1, '计算机网络',    3, 5, 'learning'),
(1, 1, 'systemd',      4, 5, 'learning'),
(1, 1, 'Nginx',        4, 5, 'learning'),
(1, 1, 'Docker',       4, 5, 'learning'),
(1, 1, 'CI/CD',        2, 5, 'learning'),
(1, 1, 'Monitoring',   1, 5, 'learning'),
(1, 1, 'Kubernetes',   1, 5, 'learning');

-- 4. 学习任务 (10 个, 状态合理分配)
-- done: Linux 进程管理 / systemd / journalctl / Nginx Reverse Proxy / Docker Compose
-- doing: Docker Network / GitHub Actions
-- todo: Prometheus / Grafana / Kubernetes 基础

INSERT INTO tasks (user_id, type, title, description, status, priority, due_date, track_id, skill_id, completed_at, sort_order) VALUES
(1, 'learning', 'Linux 进程管理',     '阶段1 · Linux 基础', 'done',  2, '2026-06-10', 1, 1, '2026-06-10 20:00:00', 1),
(1, 'learning', 'systemd',            '阶段3 · systemd',   'done',  3, '2026-07-05', 1, 3, '2026-07-05 21:00:00', 2),
(1, 'learning', 'journalctl',         '阶段3 · systemd',   'done',  2, '2026-07-08', 1, 3, '2026-07-08 19:30:00', 3),
(1, 'learning', 'Nginx Reverse Proxy','阶段4 · Nginx',     'done',  3, '2026-07-20', 1, 4, '2026-07-20 22:00:00', 4),
(1, 'learning', 'Docker Compose',     '阶段5 · Docker',    'done',  3, '2026-08-01', 1, 5, '2026-08-01 21:30:00', 5),
(1, 'learning', 'Docker Network',     '阶段5 · Docker',    'in_progress', 3, CURDATE(), 1, 5, NULL, 6),
(1, 'learning', 'GitHub Actions',     '阶段6 · CI/CD',     'in_progress', 2, CURDATE() + INTERVAL 1 DAY, 1, 6, NULL, 7),
(1, 'learning', 'Prometheus',         '阶段7 · Monitoring','todo',  2, CURDATE() + INTERVAL 2 DAY, 1, 7, NULL, 8),
(1, 'learning', 'Grafana',            '阶段7 · Monitoring','todo',  1, CURDATE() + INTERVAL 3 DAY, 1, 7, NULL, 9),
(1, 'learning', 'Kubernetes 基础',     '阶段8 · Kubernetes','todo', 2, CURDATE() + INTERVAL 5 DAY, 1, 8, NULL, 10);

-- 5. 项目 (首页 Featured 联动, 2 个真实项目)
INSERT INTO projects (user_id, name, description, tech_stack, status, progress, featured) VALUES
(1, 'Miglore OS',      '个人成长操作系统 — 学习、求职、项目、任务一体化', 'Svelte · Flask · MySQL', 'active', 12, 1),
(1, 'DevOps Lab',      'Nginx / systemd / Docker Compose 实操实验室',   'Nginx · Docker · MySQL', 'active', 80, 1);
