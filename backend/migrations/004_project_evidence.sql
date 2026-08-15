-- Migration 004: 项目证据库 (project_evidence / interview_evidence / project_milestones)
-- 日期: 2026-08-15 | 目标: 仅开发库 miglore_os (用户第七阶段授权)
-- 前置检查: 表不存在才创建; skills.id/projects.id 均为 BIGINT UNSIGNED PK (已验证)

CREATE TABLE IF NOT EXISTS project_evidence (
    id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id          BIGINT UNSIGNED NOT NULL,
    project_id       BIGINT UNSIGNED NOT NULL,
    title            VARCHAR(200) NOT NULL,
    category         ENUM('architecture','linux','docker','network','ci_cd','monitoring','database','security','troubleshooting') NOT NULL DEFAULT 'docker',
    description      TEXT NULL COMMENT '做了什么',
    technical_detail TEXT NULL COMMENT '技术细节',
    result           TEXT NULL COMMENT '结果/量化指标',
    deleted_at       DATETIME NULL,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_evidence_user (user_id),
    INDEX idx_evidence_project (project_id),
    CONSTRAINT fk_evidence_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_evidence_project FOREIGN KEY (project_id) REFERENCES projects(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS interview_evidence (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    project_id   BIGINT UNSIGNED NOT NULL,
    evidence_id  BIGINT UNSIGNED NULL COMMENT '关联技术证据 (可空)',
    skill_id     BIGINT UNSIGNED NULL COMMENT '关联现有 skills 表 (skills.id = BIGINT UNSIGNED, 已验证)',
    question     TEXT NOT NULL,
    answer       TEXT NOT NULL,
    deleted_at   DATETIME NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_interview_evidence_user (user_id),
    INDEX idx_interview_evidence_project (project_id),
    INDEX idx_interview_evidence_skill (skill_id),
    CONSTRAINT fk_iev_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_iev_project FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT fk_iev_evidence FOREIGN KEY (evidence_id) REFERENCES project_evidence(id),
    CONSTRAINT fk_iev_skill   FOREIGN KEY (skill_id)   REFERENCES skills(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS project_milestones (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT UNSIGNED NOT NULL,
    project_id  BIGINT UNSIGNED NOT NULL,
    title       VARCHAR(200) NOT NULL,
    status      ENUM('done','current','todo') NOT NULL DEFAULT 'todo',
    sort_order  INT NOT NULL DEFAULT 0,
    achieved_at DATE NULL,
    deleted_at  DATETIME NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_milestones_user (user_id),
    INDEX idx_milestones_project (project_id),
    CONSTRAINT fk_milestones_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_milestones_project FOREIGN KEY (project_id) REFERENCES projects(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
