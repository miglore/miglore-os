"""Miglore OS — Flask REST API (V1.2: Learning 模块真实数据闭环)

认证: 暂无 (单用户系统, USER_ID=1 固定, JWT 后置到 V1.1)
开发环境: 127.0.0.1:5001, 数据库 miglore_os (与生产完全隔离)
"""

import os
import time
from datetime import datetime, date

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

load_dotenv()

app = Flask(__name__)

# ---------- Prometheus metrics ----------
HTTP_REQUESTS = Counter(
    "http_requests_total", "HTTP requests total", ["method", "path", "status"]
)
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "path"]
)


@app.before_request
def _record_start():
    request._miglore_start = time.perf_counter()


@app.after_request
def _record_metrics(resp):
    path = request.url_rule.rule if request.url_rule else request.path
    method = request.method
    status = str(resp.status_code)
    HTTP_REQUESTS.labels(method=method, path=path, status=status).inc()
    duration = time.perf_counter() - getattr(request, "_miglore_start", time.perf_counter())
    HTTP_LATENCY.labels(method=method, path=path).observe(duration)
    return resp


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


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


@app.post("/api/tasks")
def create_task():
    """创建任务 (测试/日常使用)。"""
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "title required"}}), 422
    task_type = body.get("type", "daily")
    if task_type not in {"learning", "project", "daily"}:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid type: {task_type}"}}), 422
    status = body.get("status", "todo")
    if status not in TASK_STATUS:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid status: {status}"}}), 422
    task_id = execute(
        """INSERT INTO tasks (user_id, type, title, description, status, priority, due_date, track_id, skill_id, project_id, sort_order)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            USER_ID, task_type, title,
            body.get("description"), status,
            int(body.get("priority", 2)),
            body.get("due_date") or None,
            body.get("track_id"), body.get("skill_id"), body.get("project_id"),
            int(body.get("sort_order", 0)),
        ),
    )
    return jsonify({"data": {"task": get_task(task_id)}}), 201


# ========== Study Logs ==========

import re as _re

GENERATED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "generated-posts"))


def slugify(title: str) -> str:
    """中文保留, 其余转小写+连字符。"""
    s = _re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.strip().lower(), flags=_re.UNICODE)
    s = _re.sub(r"-+", "-", s).strip("-")
    return s or "post"


def make_post_markdown(log: dict, task: dict | None) -> str:
    """生成 Hexo 兼容 front-matter + 正文。"""
    title = log["title"]
    date_str = (log["created_at"] or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    tags = []
    if task and task.get("skill_name"):
        tags.append(task["skill_name"])
    if task and task.get("track_name"):
        tags.append(task["track_name"])
    tags = list(dict.fromkeys(tags)) or ["学习"]
    tag_lines = "\n".join(f"  - {t}" for t in tags)
    content = log["content"]
    task_title = task["title"] if task else "-"
    return f"""---
title: "{title}"
date: "{date_str}"
categories:
  - 学习
tags:
{tag_lines}
---

# {title}

## 今天学到了什么

{content}

## 相关任务

{task_title}
"""


def generate_markdown(log: dict, task: dict | None) -> tuple[str, str]:
    """写入 generated-posts/, 返回 (filename, abspath)。"""
    os.makedirs(GENERATED_DIR, exist_ok=True)
    filename = f"{log['log_date']}-{slugify(log['title'])}.md"
    path = os.path.join(GENERATED_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_post_markdown(log, task))
    return filename, path


def execute_transaction(statements: list[tuple[str, tuple]]) -> int:
    """多语句原子执行, 返回最后一条的 lastrowid。"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            last_id = None
            for sql, params in statements:
                cur.execute(sql, params)
                last_id = cur.lastrowid
            conn.commit()
            return int(last_id or 0)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


_LOG_SQL = """
SELECT l.*, t.title AS task_title
FROM study_logs l
LEFT JOIN tasks t ON t.id = l.task_id AND t.deleted_at IS NULL
WHERE l.user_id = %s AND l.deleted_at IS NULL
"""


def get_study_log(log_id: int) -> dict | None:
    return query_one(_LOG_SQL + " AND l.id = %s", (USER_ID, log_id))


@app.post("/api/study-logs")
def create_study_log():
    """保存学习记录 (事务: 落库 + 关联任务置为 done) + 生成 Markdown。"""
    body = request.get_json(silent=True) or {}
    task_id = body.get("task_id")
    content = (body.get("content") or "").strip()
    if not task_id or not content:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "task_id and content required"}}), 422
    task = get_task(task_id)
    if not task:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "task not found"}}), 404

    title = (body.get("title") or "").strip() or task["title"]
    log_date = body.get("log_date") or date.today().isoformat()
    duration = body.get("duration_min")

    log_id = execute_transaction([
        (
            "INSERT INTO study_logs (user_id, log_date, task_id, title, content, duration_min, track_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (USER_ID, log_date, task_id, title, content, duration, task["track_id"]),
        )
    ])
    # 闭环: 记录学习后任务完成
    if task["status"] != "done":
        execute(
            "UPDATE tasks SET status = 'done', completed_at = NOW(), updated_at = NOW() "
            "WHERE id = %s AND user_id = %s",
            (task_id, USER_ID),
        )

    log = get_study_log(log_id) or {}
    filename, path = generate_markdown(log, task)
    return jsonify({
        "data": {
            "log": log,
            "task": get_task(task_id),
            "markdown": {"filename": filename, "path": path},
        }
    }), 201


@app.get("/api/study-logs")
def list_study_logs():
    """学习记录列表, 支持 ?task_id= &limit=。"""
    where = []
    params: list = [USER_ID]
    task_id = request.args.get("task_id")
    if task_id:
        where.append("l.task_id = %s")
        params.append(int(task_id))
    limit = request.args.get("limit", type=int)
    sql = _LOG_SQL + (" AND " + " AND ".join(where) if where else "") + " ORDER BY l.log_date DESC, l.id DESC"
    if limit:
        sql += " LIMIT %s"
        params.append(limit)
    return jsonify({"data": {"logs": query(sql, tuple(params))}})


@app.get("/api/study-logs/<int:log_id>")
def get_study_log_api(log_id: int):
    log = get_study_log(log_id)
    if not log:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "study log not found"}}), 404
    return jsonify({"data": {"log": log}})


@app.patch("/api/study-logs/<int:log_id>")
def patch_study_log(log_id: int):
    body = request.get_json(silent=True) or {}
    log = get_study_log(log_id)
    if not log:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "study log not found"}}), 404

    updates = []
    params: list = []
    for field in ("content", "title", "duration_min", "mood", "log_date"):
        if field in body and body[field] is not None:
            updates.append(f"{field} = %s")
            params.append(body[field])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422
    params.append(log_id)
    execute(
        "UPDATE study_logs SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s",
        tuple(params) + (USER_ID,),
    )
    return jsonify({"data": {"log": get_study_log(log_id)}})


# ========== Career (求职: 方向/投递/面试) ==========

from jd_analyzer import analyze_jd  # noqa: E402

DIR_STATUS = {"active", "paused", "closed"}
APP_STATUS = {"draft", "applied", "interviewing", "offer", "rejected", "withdrawn"}
IVW_STATUS = {"pending", "passed", "failed", "offered"}

_APP_SQL = """
SELECT a.*, d.name AS direction_name
FROM job_applications a
LEFT JOIN career_directions d ON d.id = a.direction_id AND d.deleted_at IS NULL
WHERE a.user_id = %s AND a.deleted_at IS NULL
"""

_IVW_SQL = """
SELECT i.*, a.company, a.position
FROM interviews i
JOIN job_applications a ON a.id = i.application_id AND a.deleted_at IS NULL
WHERE i.user_id = %s AND i.deleted_at IS NULL
"""


@app.get("/api/career")
def career():
    """求职聚合: 方向 + 统计 + 最近投递 + 待面试 + 最近面试。"""
    directions = query(
        "SELECT * FROM career_directions WHERE user_id = %s AND deleted_at IS NULL ORDER BY sort_order, id",
        (USER_ID,),
    )
    # 每个方向的投递统计
    dir_stats = query(
        "SELECT direction_id, COUNT(*) cnt FROM job_applications "
        "WHERE user_id = %s AND deleted_at IS NULL GROUP BY direction_id",
        (USER_ID,),
    )
    stats_map = {r["direction_id"]: r["cnt"] for r in dir_stats}
    for d in directions:
        d["application_count"] = stats_map.get(d["id"], 0)

    # 总览统计
    stats = query_one(
        """
        SELECT
          COUNT(*) AS total,
          SUM(status IN ('applied','interviewing')) AS active,
          SUM(status = 'interviewing') AS interviewing,
          SUM(status = 'offer') AS offers,
          SUM(status = 'rejected') AS rejected
        FROM job_applications
        WHERE user_id = %s AND deleted_at IS NULL
        """,
        (USER_ID,),
    ) or {}
    for k in ("total", "active", "interviewing", "offers", "rejected"):
        stats.setdefault(k, 0)
        stats[k] = int(stats[k] or 0)  # SUM/COUNT 可能返回 str/Decimal
    stats["pending_interviews"] = int((query_one(
        "SELECT COUNT(*) c FROM interviews i JOIN job_applications a ON a.id = i.application_id "
        "WHERE i.user_id = %s AND i.deleted_at IS NULL AND a.deleted_at IS NULL "
        "AND i.result = 'pending' AND i.scheduled_at >= NOW()",
        (USER_ID,),
    ) or {}).get("c") or 0)

    now = datetime.now()
    upcoming = query(
        _IVW_SQL + " AND i.result = 'pending' AND i.scheduled_at >= %s ORDER BY i.scheduled_at LIMIT 5",
        (USER_ID, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    recent_apps = query(_APP_SQL + " ORDER BY a.applied_at DESC, a.id DESC LIMIT 5", (USER_ID,))
    recent_ivws = query(_IVW_SQL + " ORDER BY i.scheduled_at DESC, i.id DESC LIMIT 5", (USER_ID,))

    return jsonify({
        "data": {
            "directions": directions,
            "stats": stats,
            "recent_applications": recent_apps,
            "upcoming_interviews": upcoming,
            "recent_interviews": recent_ivws,
        }
    })


# ---- Directions ----

@app.get("/api/career/directions")
def list_directions():
    rows = query(
        "SELECT * FROM career_directions WHERE user_id = %s AND deleted_at IS NULL ORDER BY sort_order, id",
        (USER_ID,),
    )
    return jsonify({"data": {"directions": rows}})


@app.post("/api/career/directions")
def create_direction():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "name required"}}), 422
    status = body.get("status", "active")
    if status not in DIR_STATUS:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid status: {status}"}}), 422
    did = execute(
        "INSERT INTO career_directions (user_id, name, description, target_role, status, sort_order) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (USER_ID, name, body.get("description"), body.get("target_role"), status, int(body.get("sort_order", 0))),
    )
    return jsonify({"data": {"direction": query_one(
        "SELECT * FROM career_directions WHERE id = %s AND user_id = %s", (did, USER_ID))}}), 201


@app.patch("/api/career/directions/<int:did>")
def patch_direction(did: int):
    body = request.get_json(silent=True) or {}
    row = query_one("SELECT * FROM career_directions WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (did, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "direction not found"}}), 404
    updates, params = [], []
    for field in ("name", "description", "target_role", "status", "sort_order"):
        if field in body and body[field] is not None:
            if field == "status" and body[field] not in DIR_STATUS:
                return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "invalid status"}}), 422
            updates.append(f"{field} = %s")
            params.append(body[field])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422
    params += [did, USER_ID]
    execute("UPDATE career_directions SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s", tuple(params))
    return jsonify({"data": {"direction": query_one(
        "SELECT * FROM career_directions WHERE id = %s AND user_id = %s", (did, USER_ID))}})


@app.delete("/api/career/directions/<int:did>")
def delete_direction(did: int):
    row = query_one("SELECT id FROM career_directions WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (did, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "direction not found"}}), 404
    execute("UPDATE career_directions SET deleted_at = NOW(), updated_at = NOW() WHERE id = %s", (did,))
    return jsonify({"data": {"deleted": True}})


# ---- Applications ----

@app.get("/api/applications")
def list_applications():
    where = []
    params: list = [USER_ID]
    for key in ("status", "direction_id"):
        val = request.args.get(key)
        if val:
            where.append(f"a.{key} = %s")
            params.append(val)
    sql = _APP_SQL + (" AND " + " AND ".join(where) if where else "") + " ORDER BY a.applied_at DESC, a.id DESC"
    return jsonify({"data": {"applications": query(sql, tuple(params))}})


@app.post("/api/applications")
def create_application():
    body = request.get_json(silent=True) or {}
    company = (body.get("company") or "").strip()
    position = (body.get("position") or "").strip()
    if not company or not position:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "company and position required"}}), 422
    status = body.get("status", "applied")
    if status not in APP_STATUS:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid status: {status}"}}), 422
    aid = execute(
        "INSERT INTO job_applications (user_id, direction_id, company, position, city, salary, channel, url, status, applied_at, note) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            USER_ID, body.get("direction_id"), company, position, body.get("city"),
            body.get("salary"), body.get("channel"), body.get("url"), status,
            body.get("applied_at") or date.today().isoformat(), body.get("note"),
        ),
    )
    return jsonify({"data": {"application": query_one(_APP_SQL + " AND a.id = %s", (USER_ID, aid))}}), 201


@app.patch("/api/applications/<int:aid>")
def patch_application(aid: int):
    body = request.get_json(silent=True) or {}
    row = query_one("SELECT id FROM job_applications WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (aid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "application not found"}}), 404
    updates, params = [], []
    for field in ("company", "position", "city", "salary", "channel", "url", "status", "applied_at", "note", "direction_id"):
        if field in body and body[field] is not None:
            if field == "status" and body[field] not in APP_STATUS:
                return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "invalid status"}}), 422
            updates.append(f"{field} = %s")
            params.append(body[field])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422
    params += [aid, USER_ID]
    execute("UPDATE job_applications SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s", tuple(params))
    return jsonify({"data": {"application": query_one(_APP_SQL + " AND a.id = %s", (USER_ID, aid))}})


@app.delete("/api/applications/<int:aid>")
def delete_application(aid: int):
    row = query_one("SELECT id FROM job_applications WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (aid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "application not found"}}), 404
    execute("UPDATE job_applications SET deleted_at = NOW(), updated_at = NOW() WHERE id = %s", (aid,))
    return jsonify({"data": {"deleted": True}})


# ---- Interviews ----

@app.get("/api/interviews")
def list_interviews():
    where = []
    params: list = [USER_ID]
    for key in ("result", "application_id"):
        val = request.args.get(key)
        if val:
            where.append(f"i.{key} = %s")
            params.append(val)
    sql = _IVW_SQL + (" AND " + " AND ".join(where) if where else "") + " ORDER BY i.scheduled_at DESC, i.id DESC"
    return jsonify({"data": {"interviews": query(sql, tuple(params))}})


@app.post("/api/interviews")
def create_interview():
    body = request.get_json(silent=True) or {}
    application_id = body.get("application_id")
    if not application_id:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "application_id required"}}), 422
    app = query_one("SELECT id FROM job_applications WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (application_id, USER_ID))
    if not app:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "application not found"}}), 404
    result = body.get("result", "pending")
    if result not in IVW_STATUS:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "invalid result"}}), 422
    iid = execute(
        "INSERT INTO interviews (user_id, application_id, round, scheduled_at, interviewer, result, review, note) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (USER_ID, application_id, body.get("round", "一面"), body.get("scheduled_at"),
         body.get("interviewer"), result, body.get("review"), body.get("note")),
    )
    return jsonify({"data": {"interview": query_one(_IVW_SQL + " AND i.id = %s", (USER_ID, iid))}}), 201


@app.patch("/api/interviews/<int:iid>")
def patch_interview(iid: int):
    body = request.get_json(silent=True) or {}
    row = query_one("SELECT id FROM interviews WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (iid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "interview not found"}}), 404
    updates, params = [], []
    for field in ("round", "scheduled_at", "interviewer", "result", "review", "note"):
        if field in body and body[field] is not None:
            if field == "result" and body[field] not in IVW_STATUS:
                return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "invalid result"}}), 422
            updates.append(f"{field} = %s")
            params.append(body[field])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422
    params += [iid, USER_ID]
    execute("UPDATE interviews SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s", tuple(params))
    return jsonify({"data": {"interview": query_one(_IVW_SQL + " AND i.id = %s", (USER_ID, iid))}})


@app.delete("/api/interviews/<int:iid>")
def delete_interview(iid: int):
    row = query_one("SELECT id FROM interviews WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (iid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "interview not found"}}), 404
    execute("UPDATE interviews SET deleted_at = NOW(), updated_at = NOW() WHERE id = %s", (iid,))
    return jsonify({"data": {"deleted": True}})


# ---- JD Analyzer ----

@app.post("/api/jd-analyze")
def jd_analyze():
    """Rule-based JD 分析 (非 AI): 提取关键词 vs 个人技能库。"""
    body = request.get_json(silent=True) or {}
    jd_text = (body.get("jd_text") or "").strip()
    title = (body.get("title") or "").strip()
    if not jd_text:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "jd_text required"}}), 422
    skills = query(
        "SELECT name, level, target_level, status FROM skills "
        "WHERE user_id = %s AND deleted_at IS NULL",
        (USER_ID,),
    )
    result = analyze_jd(f"{title}\n{jd_text}", skills)
    return jsonify({"data": result})


# ========== Projects + Evidence ==========

EVIDENCE_CATEGORIES = {
    "architecture", "linux", "docker", "network", "ci_cd",
    "monitoring", "database", "security", "troubleshooting",
}
MILESTONE_STATUS = {"done", "current", "todo"}


@app.get("/api/projects")
def projects():
    """项目列表 + 统计 (数量/完成/技术栈/里程碑)。"""
    rows = query(
        "SELECT * FROM projects WHERE user_id = %s AND deleted_at IS NULL ORDER BY featured DESC, id",
        (USER_ID,),
    )
    stats_row = query_one(
        """
        SELECT COUNT(*) AS total,
               SUM(status = 'done') AS done,
               COUNT(DISTINCT tech_stack) AS tech_stacks
        FROM projects WHERE user_id = %s AND deleted_at IS NULL
        """,
        (USER_ID,),
    ) or {}
    milestones = query_one(
        "SELECT COUNT(*) c FROM project_milestones WHERE user_id = %s AND deleted_at IS NULL",
        (USER_ID,),
    ) or {}
    stats = {
        "total": int(stats_row.get("total") or 0),
        "done": int(stats_row.get("done") or 0),
        "tech_stacks": int(stats_row.get("tech_stacks") or 0),
        "milestones": int(milestones.get("c") or 0),
    }
    for p in rows:
        cnt = query_one(
            "SELECT COUNT(*) c FROM project_evidence WHERE project_id = %s AND deleted_at IS NULL",
            (p["id"],),
        ) or {}
        p["evidence_count"] = int(cnt.get("c") or 0)
    return jsonify({"data": {"projects": rows, "stats": stats}})


@app.get("/api/projects/<int:pid>")
def project_detail(pid: int):
    """项目详情: 项目 + 里程碑 + 技术证据 + 面试证据数。"""
    row = query_one(
        "SELECT * FROM projects WHERE id = %s AND user_id = %s AND deleted_at IS NULL",
        (pid, USER_ID),
    )
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "project not found"}}), 404
    milestones = query(
        "SELECT * FROM project_milestones WHERE project_id = %s AND user_id = %s AND deleted_at IS NULL "
        "ORDER BY sort_order, id",
        (pid, USER_ID),
    )
    evidence = query(
        "SELECT * FROM project_evidence WHERE project_id = %s AND user_id = %s AND deleted_at IS NULL "
        "ORDER BY id",
        (pid, USER_ID),
    )
    for e in evidence:
        ivw = query_one(
            "SELECT COUNT(*) c FROM interview_evidence WHERE evidence_id = %s AND deleted_at IS NULL",
            (e["id"],),
        ) or {}
        e["interview_count"] = int(ivw.get("c") or 0)
        e["interviews"] = query(
            """
            SELECT i.*, s.name AS skill_name
            FROM interview_evidence i
            LEFT JOIN skills s ON s.id = i.skill_id AND s.deleted_at IS NULL
            WHERE i.evidence_id = %s AND i.user_id = %s AND i.deleted_at IS NULL
            ORDER BY i.id
            """,
            (e["id"], USER_ID),
        )
    return jsonify({"data": {"project": row, "milestones": milestones, "evidence": evidence}})


# ---- Evidence ----

@app.get("/api/projects/<int:pid>/evidence")
def list_evidence(pid: int):
    rows = query(
        "SELECT * FROM project_evidence WHERE project_id = %s AND user_id = %s AND deleted_at IS NULL ORDER BY id",
        (pid, USER_ID),
    )
    return jsonify({"data": {"evidence": rows}})


@app.post("/api/projects/<int:pid>/evidence")
def create_evidence(pid: int):
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "title required"}}), 422
    category = body.get("category", "docker")
    if category not in EVIDENCE_CATEGORIES:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": f"invalid category: {category}"}}), 422
    proj = query_one("SELECT id FROM projects WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (pid, USER_ID))
    if not proj:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "project not found"}}), 404
    eid = execute(
        "INSERT INTO project_evidence (user_id, project_id, title, category, description, technical_detail, result) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (USER_ID, pid, title, category, body.get("description"), body.get("technical_detail"), body.get("result")),
    )
    return jsonify({"data": {"evidence": query_one(
        "SELECT * FROM project_evidence WHERE id = %s", (eid,))}}), 201


@app.patch("/api/evidence/<int:eid>")
def patch_evidence(eid: int):
    body = request.get_json(silent=True) or {}
    row = query_one("SELECT id FROM project_evidence WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (eid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "evidence not found"}}), 404
    updates, params = [], []
    for field in ("title", "category", "description", "technical_detail", "result"):
        if field in body and body[field] is not None:
            if field == "category" and body[field] not in EVIDENCE_CATEGORIES:
                return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "invalid category"}}), 422
            updates.append(f"{field} = %s")
            params.append(body[field])
    if not updates:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "no fields to update"}}), 422
    params += [eid, USER_ID]
    execute("UPDATE project_evidence SET " + ", ".join(updates) + ", updated_at = NOW() WHERE id = %s AND user_id = %s", tuple(params))
    return jsonify({"data": {"evidence": query_one(
        "SELECT * FROM project_evidence WHERE id = %s", (eid,))}})


@app.delete("/api/evidence/<int:eid>")
def delete_evidence(eid: int):
    row = query_one("SELECT id FROM project_evidence WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (eid, USER_ID))
    if not row:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "evidence not found"}}), 404
    execute("UPDATE project_evidence SET deleted_at = NOW(), updated_at = NOW() WHERE id = %s", (eid,))
    return jsonify({"data": {"deleted": True}})


# ---- Interview Evidence ----

@app.get("/api/evidence/<int:eid>/interview")
def list_interview_evidence(eid: int):
    """某条技术证据关联的面试问答。"""
    rows = query(
        """
        SELECT i.*, s.name AS skill_name
        FROM interview_evidence i
        LEFT JOIN skills s ON s.id = i.skill_id AND s.deleted_at IS NULL
        WHERE i.evidence_id = %s AND i.user_id = %s AND i.deleted_at IS NULL
        ORDER BY i.id
        """,
        (eid, USER_ID),
    )
    return jsonify({"data": {"interviews": rows}})


@app.post("/api/evidence/<int:eid>/interview")
def create_interview_evidence(eid: int):
    """创建面试问答 (关联证据 + 可选 skill)。"""
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    answer = (body.get("answer") or "").strip()
    if not question or not answer:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "question and answer required"}}), 422
    ev = query_one("SELECT id, project_id FROM project_evidence WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (eid, USER_ID))
    if not ev:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "evidence not found"}}), 404
    skill_id = body.get("skill_id")
    if skill_id is not None:
        sk = query_one("SELECT id FROM skills WHERE id = %s AND user_id = %s AND deleted_at IS NULL", (skill_id, USER_ID))
        if not sk:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "skill not found"}}), 404
    iid = execute(
        "INSERT INTO interview_evidence (user_id, project_id, evidence_id, skill_id, question, answer) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (USER_ID, ev["project_id"], eid, skill_id, question, answer),
    )
    row = query_one(
        """
        SELECT i.*, s.name AS skill_name
        FROM interview_evidence i
        LEFT JOIN skills s ON s.id = i.skill_id AND s.deleted_at IS NULL
        WHERE i.id = %s
        """,
        (iid,),
    )
    return jsonify({"data": {"interview": row}}), 201


# ========== 其他模块 (骨架, 后续阶段) ==========


@app.get("/api/journal")
def journal():
    return jsonify({"data": {"logs": []}})


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5001"))
    debug = bool(int(os.getenv("FLASK_DEBUG", "0")))
    app.run(host=host, port=port, debug=debug)
