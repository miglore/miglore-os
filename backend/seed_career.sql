-- Miglore OS Career 演示数据 (注入 compose 容器 mysql, 仅开发环境)
USE miglore_os;

INSERT INTO career_directions (id, user_id, name, description, target_role, status, sort_order)
VALUES (1, 1, 'DevOps / 运维开发', '云原生方向：容器化、CI/CD、监控告警', 'DevOps 工程师', 'active', 1);

INSERT INTO job_applications (user_id, direction_id, company, position, city, salary, channel, status, applied_at, note) VALUES
(1, 1, '某某云科技', '运维工程师',     '上海', '15-20K', 'BOSS直聘', 'interviewing', '2026-08-10', '一面通过，等二面'),
(1, 1, '某某数据',   'DevOps 工程师',  '杭州', '18-25K', '内推',      'interviewing', '2026-08-08', NULL),
(1, 1, '某某网络',   '云计算运维',     '上海', '13-18K', 'BOSS直聘', 'applied',      '2026-08-12', NULL),
(1, 1, '某某信息',   '运维开发',       '远程', '14-20K', '拉勾',      'rejected',     '2026-08-01', '岗位要求 k8s 生产经验');

INSERT INTO interviews (user_id, application_id, round, scheduled_at, interviewer, result, review, note) VALUES
(1, 1, '一面', '2026-08-13 14:00:00', '张工', 'passed', 'Linux/网络基础扎实', NULL),
(1, 2, '一面', '2026-08-18 10:30:00', '李工', 'pending', NULL, NULL),
(1, 1, '二面', '2026-08-20 15:00:00', '王总', 'pending', NULL, '待面试');
