-- Miglore OS V1 schema (dev database: miglore_os)
-- 依据 docs/database.md ER 设计
-- 软删除统一 deleted_at; 时间戳 created_at/updated_at

CREATE TABLE IF NOT EXISTS users (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name  VARCHAR(50)  NULL,
    avatar_url    VARCHAR(255) NULL,
    career_goal   VARCHAR(255) NULL COMMENT '首页 Hero 职业目标',
    deleted_at    DATETIME     NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learning_tracks (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT UNSIGNED NOT NULL,
    title       VARCHAR(100) NOT NULL,
    description TEXT NULL,
    status      ENUM('active','paused','completed') NOT NULL DEFAULT 'active',
    progress    INT NOT NULL DEFAULT 0 COMMENT '0-100',
    started_at  DATE NULL,
    sort_order  INT NOT NULL DEFAULT 0,
    deleted_at  DATETIME NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tracks_user (user_id),
    INDEX idx_tracks_user_status (user_id, status),
    CONSTRAINT fk_tracks_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS skills (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    track_id     BIGINT UNSIGNED NULL,
    name         VARCHAR(50) NOT NULL,
    level        TINYINT NOT NULL DEFAULT 1 COMMENT '1-5',
    target_level TINYINT NOT NULL DEFAULT 5 COMMENT '1-5',
    status       ENUM('learning','learned','idle') NOT NULL DEFAULT 'learning',
    deleted_at   DATETIME NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_skills_user (user_id),
    INDEX idx_skills_track (track_id),
    CONSTRAINT fk_skills_user  FOREIGN KEY (user_id)  REFERENCES users(id),
    CONSTRAINT fk_skills_track FOREIGN KEY (track_id) REFERENCES learning_tracks(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS projects (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT NULL,
    tech_stack  VARCHAR(255) NULL,
    repo_url    VARCHAR(500) NULL,
    status      ENUM('planning','active','paused','done','archived') NOT NULL DEFAULT 'active',
    progress    INT NOT NULL DEFAULT 0 COMMENT '0-100',
    start_date  DATE NULL,
    end_date    DATE NULL,
    featured    TINYINT NOT NULL DEFAULT 0 COMMENT '首页 Featured 标记',
    deleted_at  DATETIME NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projects_user (user_id),
    INDEX idx_projects_user_featured (user_id, featured),
    INDEX idx_projects_user_status (user_id, status),
    CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tasks (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    type         ENUM('learning','project','daily') NOT NULL DEFAULT 'daily',
    title        VARCHAR(200) NOT NULL,
    description  TEXT NULL,
    status       ENUM('todo','in_progress','done','cancelled') NOT NULL DEFAULT 'todo',
    priority     TINYINT NOT NULL DEFAULT 2 COMMENT '1低 2中 3高',
    due_date     DATE NULL,
    track_id     BIGINT UNSIGNED NULL,
    skill_id     BIGINT UNSIGNED NULL,
    project_id   BIGINT UNSIGNED NULL,
    completed_at DATETIME NULL,
    sort_order   INT NOT NULL DEFAULT 0,
    deleted_at   DATETIME NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tasks_user (user_id),
    INDEX idx_tasks_user_status (user_id, status),
    INDEX idx_tasks_user_due (user_id, due_date),
    INDEX idx_tasks_project (project_id),
    INDEX idx_tasks_track (track_id),
    CONSTRAINT fk_tasks_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_tasks_track   FOREIGN KEY (track_id)   REFERENCES learning_tracks(id),
    CONSTRAINT fk_tasks_skill   FOREIGN KEY (skill_id)   REFERENCES skills(id),
    CONSTRAINT fk_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS career_directions (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT NULL,
    target_role VARCHAR(100) NULL,
    status      ENUM('active','paused','closed') NOT NULL DEFAULT 'active',
    sort_order  INT NOT NULL DEFAULT 0,
    deleted_at  DATETIME NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_directions_user (user_id),
    INDEX idx_directions_user_status (user_id, status),
    CONSTRAINT fk_directions_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS job_applications (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    direction_id BIGINT UNSIGNED NULL,
    company      VARCHAR(100) NOT NULL,
    position     VARCHAR(100) NOT NULL,
    city         VARCHAR(100) NULL COMMENT '城市 (migration 003)',
    salary       VARCHAR(100) NULL COMMENT '薪资 (migration 003)',
    channel      VARCHAR(50)  NULL,
    url          VARCHAR(500) NULL,
    status       ENUM('draft','applied','interviewing','offer','rejected','withdrawn') NOT NULL DEFAULT 'applied',
    applied_at   DATE NULL,
    note         TEXT NULL,
    deleted_at   DATETIME NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_apps_user (user_id),
    INDEX idx_apps_user_status (user_id, status),
    INDEX idx_apps_direction (direction_id),
    INDEX idx_apps_applied_at (applied_at),
    CONSTRAINT fk_apps_user      FOREIGN KEY (user_id)      REFERENCES users(id),
    CONSTRAINT fk_apps_direction FOREIGN KEY (direction_id) REFERENCES career_directions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS interviews (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id        BIGINT UNSIGNED NOT NULL,
    application_id BIGINT UNSIGNED NOT NULL,
    round          VARCHAR(30) NOT NULL DEFAULT '一面',
    scheduled_at   DATETIME NULL,
    interviewer    VARCHAR(100) NULL,
    result         ENUM('pending','passed','failed','offered') NOT NULL DEFAULT 'pending',
    review         TEXT NULL COMMENT '复盘',
    note           TEXT NULL,
    deleted_at     DATETIME NULL,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_interviews_user (user_id),
    INDEX idx_interviews_app (application_id),
    INDEX idx_interviews_app_sched (application_id, scheduled_at),
    CONSTRAINT fk_interviews_user  FOREIGN KEY (user_id)        REFERENCES users(id),
    CONSTRAINT fk_interviews_app   FOREIGN KEY (application_id) REFERENCES job_applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS study_logs (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    log_date     DATE NOT NULL,
    task_id      BIGINT UNSIGNED NULL COMMENT '关联学习任务 (migration 002)',
    title        VARCHAR(200) NULL COMMENT '记录标题, 默认取任务标题',
    content      TEXT NOT NULL,
    duration_min INT NULL,
    mood         TINYINT NULL COMMENT '1-5',
    track_id     BIGINT UNSIGNED NULL,
    project_id   BIGINT UNSIGNED NULL,
    deleted_at   DATETIME NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_logs_user (user_id),
    INDEX idx_logs_user_date (user_id, log_date),
    INDEX idx_logs_task (task_id),
    INDEX idx_logs_track (track_id),
    INDEX idx_logs_project (project_id),
    CONSTRAINT fk_logs_user    FOREIGN KEY (user_id)    REFERENCES users(id),
    CONSTRAINT fk_logs_task    FOREIGN KEY (task_id)    REFERENCES tasks(id),
    CONSTRAINT fk_logs_track   FOREIGN KEY (track_id)   REFERENCES learning_tracks(id),
    CONSTRAINT fk_logs_project FOREIGN KEY (project_id) REFERENCES projects(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
