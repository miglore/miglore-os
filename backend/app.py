"""Miglore OS — Flask REST API (V1 bootstrap)

第一批接口: health + 6 个聚合只读接口(返回契约骨架空结构)。
开发环境: 127.0.0.1:5001, 数据库 miglore_os (与生产完全隔离)。
"""

import os

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173")
CORS(app, origins=[o.strip() for o in CORS_ORIGINS.split(",") if o.strip()])


def db_config() -> dict:
    """读取数据库连接配置(仅开发库 miglore_os)。"""
    return {
        "host": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "port": int(os.getenv("DATABASE_PORT", "3306")),
        "user": os.getenv("DATABASE_USER", "miglore_os"),
        "password": os.getenv("DATABASE_PASSWORD", ""),
        "database": os.getenv("DATABASE_NAME", "miglore_os"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 3,
    }


def ping_db() -> bool:
    """只读连通性检查。"""
    try:
        conn = pymysql.connect(**db_config())
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        return True
    except Exception:
        return False


@app.get("/api/health")
def health():
    db_ok = ping_db()
    return jsonify({
        "data": {
            "status": "ok" if db_ok else "degraded",
            "service": "miglore-os-backend",
            "database": "connected" if db_ok else "unreachable",
            "time": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        }
    })


@app.get("/api/dashboard")
def dashboard():
    """首页聚合 — V1 骨架(空数据), 契约见 docs/api.md。"""
    return jsonify({
        "data": {
            "hero": None,
            "continue_learning": [],
            "learning_progress": [],
            "featured_projects": [],
            "today_tasks": [],
            "recent_activity": [],
            "career_status": {},
        }
    })


@app.get("/api/learning")
def learning():
    return jsonify({"data": {"tracks": []}})


@app.get("/api/tasks")
def tasks():
    return jsonify({"data": {"tasks": []}})


@app.get("/api/projects")
def projects():
    return jsonify({"data": {"projects": []}})


@app.get("/api/career")
def career():
    return jsonify({"data": {"summary": {}, "directions": []}})


@app.get("/api/journal")
def journal():
    return jsonify({"data": {"logs": []}})


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5001"))
    debug = bool(int(os.getenv("FLASK_DEBUG", "0")))
    app.run(host=host, port=port, debug=debug)
