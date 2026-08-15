"""pytest fixtures — 独立测试数据库 miglore_os_test, 不依赖开发/生产库。

加载顺序:
1. 从 backend/.env 读取连接信息 (真实密码只在本地, 不入库)
2. 强制 DATABASE_NAME=miglore_os_test (独立测试库)
3. 再 import app (app.py 内 load_dotenv 不覆盖已设变量)
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# 1. 加载 .env 获取连接凭据
load_dotenv(BACKEND_DIR / ".env")

# 2. 强制测试库 (即使 .env 配置了其他库)
os.environ["DATABASE_NAME"] = "miglore_os_test"
os.environ.setdefault("DATABASE_HOST", "127.0.0.1")
os.environ.setdefault("DATABASE_PORT", "3306")
os.environ.setdefault("DATABASE_USER", "miglore_os")

# 3. 导入 app 模块
sys.path.insert(0, str(BACKEND_DIR))
import app as app_module  # noqa: E402

# 测试库 schema (幂等 CREATE TABLE IF NOT EXISTS)
SCHEMA_SQL = BACKEND_DIR / "schema.sql"

# 最小基础数据 (测试用, 每条用例前重灌)
BASE_SEED = [
    ("INSERT INTO users (id, username, email, password_hash, display_name, career_goal) "
     "VALUES (1, 'tester', 't@test.local', 'x', 'tester', 'DevOps 工程师')", ()),
    ("INSERT INTO learning_tracks (id, user_id, title, status, sort_order) "
     "VALUES (1, 1, '测试路线', 'active', 1)", ()),
    ("INSERT INTO skills (id, user_id, track_id, name, level, target_level) "
     "VALUES (1, 1, 1, 'Linux', 3, 5)", ()),
    ("INSERT INTO learning_tracks (id, user_id, title, status, sort_order) "
     "VALUES (2, 1, 'Linux Engineer Roadmap V2', 'active', 2)", ()),
    ("INSERT INTO tasks (id, user_id, type, title, status, priority, track_id, skill_id) "
     "VALUES (1, 1, 'learning', '测试任务A', 'done', 2, 1, 1), "
     "(2, 1, 'learning', '测试任务B', 'in_progress', 3, 1, 1), "
     "(3, 1, 'learning', '测试任务C', 'todo', 1, 1, 1)", ()),
    ("INSERT INTO tasks (id, user_id, type, title, status, track_id, skill_id, sort_order) "
     "VALUES (101, 1, 'learning', '05 mkdir', 'todo', 2, 1, 5), "
     "(102, 1, 'learning', '10 cat', 'todo', 2, 1, 10)", ()),
    ("INSERT INTO projects (id, user_id, name, tech_stack, status, progress, featured) "
     "VALUES (1, 1, '测试项目', 'Svelte·Flask·Docker', 'active', 50, 1)", ()),
]

TRUNCATE = [
    "SET FOREIGN_KEY_CHECKS = 0",
    "TRUNCATE interview_evidence",
    "TRUNCATE project_evidence",
    "TRUNCATE project_milestones",
    "TRUNCATE study_logs",
    "TRUNCATE tasks",
    "TRUNCATE skills",
    "TRUNCATE learning_tracks",
    "TRUNCATE projects",
    "TRUNCATE career_directions",
    "TRUNCATE job_applications",
    "TRUNCATE interviews",
    "TRUNCATE users",
    "SET FOREIGN_KEY_CHECKS = 1",
]


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """建测试库表结构 (一次): 缺任一核心表即执行完整 schema.sql (幂等)。"""
    conn = app_module.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM information_schema.tables "
                        "WHERE table_schema = DATABASE() AND table_name = 'project_evidence'")
            if cur.fetchone()["COUNT(*)"] == 0:
                # 先整行过滤注释与 USE 切换 (防串库), 再按分号拆分执行
                clean = "\n".join(
                    line for line in SCHEMA_SQL.read_text(encoding="utf-8").splitlines()
                    if not line.strip().startswith("--")
                    and not line.strip().upper().startswith("USE ")
                )
                for raw in clean.split(";"):
                    stmt = raw.strip()
                    if stmt:
                        cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def db():
    """每用例重置数据并灌入基础 seed。"""
    conn = app_module.get_conn()
    try:
        with conn.cursor() as cur:
            for stmt in TRUNCATE:
                cur.execute(stmt)
            for sql, params in BASE_SEED:
                cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
    yield


@pytest.fixture()
def client(db):
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture()
def md_tmp(tmp_path, monkeypatch):
    """Markdown 生成目录隔离到临时目录。"""
    monkeypatch.setattr(app_module, "GENERATED_DIR", str(tmp_path))
    return tmp_path
