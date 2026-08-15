"""Miglore OS — Flask REST API (V1.2: Learning 模块真实数据闭环)

认证: 暂无 (单用户系统, USER_ID=1 固定, JWT 后置到 V1.1)
开发环境: 127.0.0.1:5001, 数据库 miglore_os (与生产完全隔离)
"""

import os
from datetime import datetime, date

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)


class ISOJSONProvider(DefaultJSONProvider):
    """date/datetime 序列化为 ISO 字符串, 便于前端解析。"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)


app.json = ISOJSONProvider(app)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173")
CORS(app, origins=[o.strip() for o in CORS_ORIGINS.split(",") if o.strip()])

# 单用户系统: 固定用户 id (V1.1 接入认证后替换为 session user)
USER_ID = 1

TASK_STATUS = {"todo", "in_progress", "done", "cancelled"}
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def db_config() -> dict:
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


def get_conn():
    return pymysql.connect(**db_config())


def query(sql: str, params=()) -> list:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql: str, params=()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=()) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


# ---------- 任务行序列化 (补关联名) ----------

_TASK_SQL = """
SELECT t.*, tr.title AS track_name, s.name AS skill_name
FROM tasks t
LEFT JOIN learning_tracks tr ON tr.id = t.track_id AND tr.deleted_at IS NULL
LEFT JOIN skills s ON s.id = t.skill_id AND s.deleted_at IS NULL
WHERE t.user_id = %s AND t.deleted_at IS NULL
"""


def get_task(task_id: int) -> dict | None:
    return query_one(_TASK_SQL + " AND t.id = %s", (USER_ID, task_id))


# ---------- 聚合统计 ----------

def track_stats(track_id: int) -> dict:
    """某路线任务统计: done/total/percent。"""
    row = query_one(
        """
        SELECT
          COUNT(*) AS total,
          SUM(status = 'done') AS done
        FROM tasks
        WHERE user_id = %s AND track_id = %s AND deleted_at IS NULL
        """,
        (USER_ID, track_id),
    ) or {}
    total = int(row.get("total") or 0)
    done = int(row.get("done") or 0)
    return {"done": done, "total": total, "percent": round(done / total * 100) if total else 0}


def streak_days() -> int:
    """从 study_logs 计算连续学习天数 (今天或昨天起连续)。"""
    logs = query(
        "SELECT log_date FROM study_logs WHERE user_id = %s AND deleted_at IS NULL ORDER BY log_date DESC",
        (USER_ID,),
    )
    dates = {r["log_date"] for r in logs}
    if not dates:
        return 0
    today = date.today()
    cursor = today if today in dates else today - __import__("datetime").timedelta(days=1)
    if cursor not in dates:
        return 0
    n = 0
    while cursor in dates:
        n += 1
        cursor -= __import__("datetime").timedelta(days=1)
    return n


# ========== 健康检查 ==========

@app.get("/api/health")
def health():
    db_ok = False
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        db_ok = True
    except Exception:
        pass
    return jsonify({
        "data": {
            "status": "ok" if db_ok else "degraded",
            "service": "miglore-os-backend",
            "database": "connected" if db_ok else "unreachable",
            "time": datetime.now().isoformat(timespec="seconds"),
        }
    })


# ========== Learning ==========

@app.get("/api/learning")
def learning():
    """学习路线 + 当前路线 + 总体进度 + 学习任务。"""
    tracks = query(
        "SELECT * FROM learning_tracks WHERE user_id = %s AND deleted_at IS NULL ORDER BY sort_order, id",
        (USER_ID,),
    )
    tasks = query(
        _TASK_SQL + " AND t.type = 'learning' ORDER BY t.sort_order, t.id",
        (USER_ID,),
    )

    current = None
    if tracks:
        # 当前路线: 优先 active, 否则第一个
        active = next((t for t in tracks if t["status"] == "active"), tracks[0])
        stats = track_stats(active["id"])
        # 当前阶段: 取第一个进行中任务的阶段描述, 否则最近 done
        doing = next((t for t in tasks if t["status"] == "in_progress"), None)
        last_done = next((t for t in tasks if t["status"] == "done"), None)
        stage = (doing or last_done or {}).get("description") or "开始学习"
        current = {
            "id": active["id"],
            "title": active["title"],
            "description": active["description"],
            "stage": stage,
            "progress": stats["percent"],
            "stats": stats,
        }

    overall = track_stats(tracks[0]["id"]) if tracks else {"done": 0, "total": 0, "percent": 0}

    return jsonify({
        "data": {
            "tracks": tracks,
            "current": current,
            "progress": overall,
            "tasks": tasks,
        }
    })


# ========== Tasks ==========

@app.get("/api/tasks")
def tasks():
    """任务列表, 支持 ?status= &type= &limit=。"""
    where = []  # _TASK_SQL 已含 user_id + deleted_at 条件
    params: list = [USER_ID]
    status = request.args.get("status")
    task_type = request.args.get("type")
    if status:
        where.append("t.status = %s")
        params.append(status)
    if task_type:
        where.append("t.type = %s")
        params.append(task_type)
    limit = request.args.get("limit", type=int)
    sql = _TASK_SQL + (" AND " + " AND ".join(where) if where else "")
    sql += " ORDER BY t.sort_order, t.id"
    if limit:
        sql += " LIMIT %s"
        params.append(limit)
    return jsonify({"data": {"tasks": query(sql, tuple(params))}})


@app.patch("/api/tasks/<int:task_id>")
def patch_task(task_id: int):
    """更新任务 (至少支持 status)。status=done 时记录 completed_at。"""
    body = request.get_json(silent=True) or {}
    task = get_task(task_id)
    if not task:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "task not found"}}), 404

    updates = []
    params: list = []
    if "status" in body:
        new_status = body["status"]
        if new_status not in TASK_STATUS:
            return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid status: {new_status}"}}), 422
        updates.append("status = %s")
        params.append(new_status)
        if new_status == "done":
            updates.append("completed_at = NOW()")
        else:
            updates.append("completed_at = NULL")
    if "priority" in body:
        updates.append("priority = %s")
        params.append(int(body["priority"]))
    if "due_date" in body:
        updates.append("due_date = %s")
        params.append(body["due_date"] or None)
    if "title" in body:
        updates.append("title = %s")
        params.append(body["title"])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422

    params.append(task_id)
    execute(
        "UPDATE tasks SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s",
        tuple(params) + (USER_ID,),
    )
    return jsonify({"data": {"task": get_task(task_id)}})


# ========== Dashboard ==========

@app.get("/api/dashboard")
def dashboard():
    """首页聚合 — 真实数据 (learning/tasks/projects/study_logs)。"""
    today = date.today()
    user = query_one(
        "SELECT career_goal FROM users WHERE id = %s AND deleted_at IS NULL", (USER_ID,)
    )
    tracks = query(
        "SELECT * FROM learning_tracks WHERE user_id = %s AND deleted_at IS NULL ORDER BY sort_order, id",
        (USER_ID,),
    )

    # Hero
    hero = None
    if user and tracks:
        active = next((t for t in tracks if t["status"] == "active"), tracks[0])
        stats = track_stats(active["id"])
        hero = {
            "date": f"{today.month}月{today.day}日",
            "weekday": WEEKDAYS[today.weekday()],
            "streak_days": streak_days(),
            "career_goal": user["career_goal"] or "DevOps 工程师",
            "active_track": {
                "id": active["id"],
                "title": active["title"],
                "progress": stats["percent"],
            },
        }

    # Continue Learning: 未完成学习任务 (进行中优先)
    continue_learning = query(
        _TASK_SQL + """
          AND t.type = 'learning' AND t.status IN ('todo', 'in_progress')
          ORDER BY (t.status = 'in_progress') DESC, t.due_date ASC, t.sort_order
          LIMIT 4
        """,
        (USER_ID,),
    )

    # Learning Progress: 技能 (前 6)
    learning_progress = query(
        "SELECT * FROM skills WHERE user_id = %s AND deleted_at IS NULL ORDER BY level DESC, id LIMIT 6",
        (USER_ID,),
    )

    # Featured Projects
    featured_projects = query(
        "SELECT * FROM projects WHERE user_id = %s AND featured = 1 AND deleted_at IS NULL ORDER BY id LIMIT 3",
        (USER_ID,),
    )

    # Today's Tasks: 截止今天未完成, 优先级排序
    today_tasks = query(
        _TASK_SQL + """
          AND t.due_date = %s AND t.status != 'done'
          ORDER BY t.priority DESC, t.sort_order
          LIMIT 6
        """,
        (USER_ID, today.isoformat()),
    )

    # Recent Activity: 学习日志
    recent_activity = query(
        "SELECT * FROM study_logs WHERE user_id = %s AND deleted_at IS NULL ORDER BY log_date DESC, id DESC LIMIT 5",
        (USER_ID,),
    )

    return jsonify({
        "data": {
            "hero": hero,
            "continue_learning": continue_learning,
            "learning_progress": learning_progress,
            "featured_projects": featured_projects,
            "today_tasks": today_tasks,
            "recent_activity": recent_activity,
            "career_status": {},  # Career 模块后续阶段
        }
    })


# ========== 其他模块 (骨架, 后续阶段) ==========

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
