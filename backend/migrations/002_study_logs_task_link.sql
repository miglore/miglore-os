-- Migration 002: study_logs 增加任务关联 (task_id/title)
-- 日期: 2026-08-15 | 目标: 仅开发库 miglore_os
-- 前置备份: backend/migrations/backup_study_logs_20260815_215357.sql
-- 依据用户第三阶段确认 (差异报告后授权)

USE miglore_os;

ALTER TABLE study_logs
  ADD COLUMN task_id BIGINT UNSIGNED NULL AFTER log_date,
  ADD COLUMN title VARCHAR(200) NULL AFTER task_id,
  ADD INDEX idx_logs_task (task_id);

-- task_id 类型与 tasks.id (BIGINT UNSIGNED) 匹配, 添加外键安全
ALTER TABLE study_logs
  ADD CONSTRAINT fk_logs_task FOREIGN KEY (task_id) REFERENCES tasks(id);
