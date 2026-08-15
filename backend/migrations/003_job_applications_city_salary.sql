-- Migration 003: job_applications 增加城市/薪资 (city/salary)
-- 日期: 2026-08-15 | 目标: 仅开发库 miglore_os (用户第六阶段授权)
-- 前置备份: backend/migrations/backup_job_applications_20260815.sql

USE miglore_os;

ALTER TABLE job_applications
  ADD COLUMN city VARCHAR(100) NULL AFTER position,
  ADD COLUMN salary VARCHAR(100) NULL AFTER city;
