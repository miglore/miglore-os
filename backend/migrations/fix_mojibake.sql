-- Miglore OS — 修复 double-encoded (latin1 mojibake) 中文数据
-- 日期: 2026-08-16 | 目标: 仅开发库 miglore_os
-- 前置备份: backend/migrations/backup_miglore_os_20260816_001346.sql
-- 方法: latin1 1:1 取回原始 UTF-8 字节 → 按 utf8mb4 解码 (对正常 UTF-8 幂等, 安全)
-- 精确性: 每列仅在含 0xC3 特征字节 (double-encoded) 的行执行

USE miglore_os;

-- users
UPDATE users SET career_goal = CONVERT(CAST(CONVERT(career_goal USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(career_goal,'')) LIKE '%C3%';

-- learning_tracks
UPDATE learning_tracks SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(title,'')) LIKE '%C3%';
UPDATE learning_tracks SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(description,'')) LIKE '%C3%';

-- tasks
UPDATE tasks SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(title,'')) LIKE '%C3%';
UPDATE tasks SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(description,'')) LIKE '%C3%';

-- projects
UPDATE projects SET name = CONVERT(CAST(CONVERT(name USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(name,'')) LIKE '%C3%';
UPDATE projects SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(description,'')) LIKE '%C3%';
UPDATE projects SET tech_stack = CONVERT(CAST(CONVERT(tech_stack USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(tech_stack,'')) LIKE '%C3%';

-- career_directions
UPDATE career_directions SET name = CONVERT(CAST(CONVERT(name USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(name,'')) LIKE '%C3%';
UPDATE career_directions SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(description,'')) LIKE '%C3%';

-- job_applications
UPDATE job_applications SET company = CONVERT(CAST(CONVERT(company USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(company,'')) LIKE '%C3%';
UPDATE job_applications SET position = CONVERT(CAST(CONVERT(position USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(position,'')) LIKE '%C3%';
UPDATE job_applications SET city = CONVERT(CAST(CONVERT(city USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(city,'')) LIKE '%C3%';
UPDATE job_applications SET salary = CONVERT(CAST(CONVERT(salary USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(salary,'')) LIKE '%C3%';
UPDATE job_applications SET channel = CONVERT(CAST(CONVERT(channel USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(channel,'')) LIKE '%C3%';
UPDATE job_applications SET note = CONVERT(CAST(CONVERT(note USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(note,'')) LIKE '%C3%';

-- interviews
UPDATE interviews SET round = CONVERT(CAST(CONVERT(round USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(round,'')) LIKE '%C3%';
UPDATE interviews SET interviewer = CONVERT(CAST(CONVERT(interviewer USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(interviewer,'')) LIKE '%C3%';
UPDATE interviews SET review = CONVERT(CAST(CONVERT(review USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(review,'')) LIKE '%C3%';
UPDATE interviews SET note = CONVERT(CAST(CONVERT(note USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(note,'')) LIKE '%C3%';

-- project_evidence
UPDATE project_evidence SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(title,'')) LIKE '%C3%';
UPDATE project_evidence SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(description,'')) LIKE '%C3%';
UPDATE project_evidence SET technical_detail = CONVERT(CAST(CONVERT(technical_detail USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(technical_detail,'')) LIKE '%C3%';
UPDATE project_evidence SET result = CONVERT(CAST(CONVERT(result USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(result,'')) LIKE '%C3%';

-- project_milestones (title 含中文的仅 Stage 描述为英文, 防御性执行)
UPDATE project_milestones SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(title,'')) LIKE '%C3%';

-- study_logs (API 写入应正常, 防御性执行)
UPDATE study_logs SET content = CONVERT(CAST(CONVERT(content USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(content,'')) LIKE '%C3%';
UPDATE study_logs SET title = CONVERT(CAST(CONVERT(title USING latin1) AS BINARY) USING utf8mb4)
  WHERE HEX(IFNULL(title,'')) LIKE '%C3%';
