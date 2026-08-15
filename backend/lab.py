"""Miglore OS — Linux Lab (隔离实验环境)

- 管理独立 lab 容器 (miglore-os-lab, ubuntu:24.04, 非特权, 独立网络, 无端口)
- exec: 一次性命令执行 (docker exec, 无 TTY)
- reset: 清空实验环境 (/tmp/miglab)
- verify: 按 L0 验证脚本检查实验产物, PASS → 任务 done + 学习记录闭环

安全: 仅操作 miglore-os-lab 容器; 容器无特权/无宿主挂载/无端口/资源受限。
"""
from __future__ import annotations

import datetime
import os

import docker  # type: ignore
from flask import request

LAB_CONTAINER = os.environ.get("LAB_CONTAINER", "miglore-os-lab")
LAB_TRACK_ID = 2  # learning_tracks.id = Linux Engineer Roadmap V2
LAB_WORKDIR = "/tmp/miglab"

# L0 验证脚本: sort_order -> sh 命令 (stdout 含 PASS 视为通过, 其余为 FAIL 提示)
L0_VERIFY: dict[int, str] = {
    1: "uname -s | grep -qi linux && echo PASS || echo FAIL:uname 未返回 linux",
    2: "cd /tmp && pwd | grep -q '/tmp' && echo PASS || echo FAIL:cd 后 pwd 非 /tmp",
    3: "ls -lah / >/dev/null 2>&1 && echo PASS || echo FAIL:ls 执行失败",
    4: "cd /tmp && pwd | grep -q /tmp && echo PASS || echo FAIL:cd /tmp 失败",
    5: "test -d /tmp/miglab && echo PASS || echo 'FAIL: 请先执行 mkdir -p /tmp/miglab'",
    6: "test -f /tmp/miglab/hello.txt && echo PASS || echo 'FAIL: 请先执行 touch /tmp/miglab/hello.txt'",
    7: "test -f /tmp/miglab/copy.txt && cmp -s /tmp/miglab/hello.txt /tmp/miglab/copy.txt && echo PASS || echo 'FAIL: 请先执行 cp /tmp/miglab/hello.txt /tmp/miglab/copy.txt'",
    8: "test -f /tmp/miglab/moved.txt && echo PASS || echo 'FAIL: 请先执行 mv /tmp/miglab/copy.txt /tmp/miglab/moved.txt'",
    9: "test ! -e /tmp/miglab/old.txt && echo PASS || echo 'FAIL: 先执行 touch /tmp/miglab/old.txt 再用 rm 删除它'",
    10: "grep -q hello /tmp/miglab/hello.txt && echo PASS || echo 'FAIL: 请先执行 echo hello > /tmp/miglab/hello.txt'",
    11: "head -1 /tmp/miglab/hello.txt | grep -q . && echo PASS || echo 'FAIL: 请先完成 07 cp 实验 (hello.txt 需有内容)'",
    12: "head -3 /tmp/miglab/hello.txt >/dev/null 2>&1 && tail -2 /tmp/miglab/hello.txt >/dev/null 2>&1 && echo PASS || echo FAIL:head/tail 执行失败",
    13: "grep -q hello /tmp/miglab/hello.txt && echo PASS || echo 'FAIL: 请先执行 echo hello > /tmp/miglab/hello.txt'",
    14: "find /tmp/miglab -name 'hello.txt' | grep -q hello && echo PASS || echo 'FAIL: 请先创建 /tmp/miglab/hello.txt'",
    15: "test -d /tmp/miglab && test -f /tmp/miglab/hello.txt && test -f /tmp/miglab/moved.txt && grep -q hello /tmp/miglab/hello.txt && echo PASS || echo 'FAIL: 请按 05-14 在 /tmp/miglab 完成全部实验'",
}


def _client() -> docker.DockerClient:
    """经 unix socket 连接宿主 Docker (仅用于 lab 容器操作)。"""
    return docker.from_env()


def _container():
    c = _client().containers.get(LAB_CONTAINER)
    if not c:
        raise RuntimeError("Lab 容器不存在")
    return c


def lab_running() -> bool:
    try:
        return _container().status == "running"
    except Exception:
        return False


def lab_exec(cmd: str, timeout: int = 15):
    """在 lab 容器执行一次性命令, 返回 (exit_code, stdout, stderr)。"""
    if not lab_running():
        return 1, "", "Lab 容器未运行, 请点击 Reset"
    try:
        c = _container()
        exit_code, output = c.exec_run(cmd=["sh", "-c", cmd], demux=True)
        stdout, stderr = output if isinstance(output, tuple) else (output, b"")
        return int(exit_code), (stdout or b"").decode("utf-8", errors="replace"), (stderr or b"").decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return 1, "", f"执行失败: {e}"


def lab_reset():
    """清空实验环境 (完全删除 /tmp/miglab, 用户需从 mkdir 重新开始)。"""
    if not lab_running():
        return False, "Lab 容器未运行"
    code, out, err = lab_exec(f"rm -rf {LAB_WORKDIR} && echo LAB_RESET_OK")
    ok = "LAB_RESET_OK" in out
    return ok, out.strip() or err.strip() or f"reset exit={code}"


# ========== 验证与闭环 ==========

def _verify_script(task) -> str | None:
    """按任务的 sort_order 取 L0 验证脚本。"""
    return L0_VERIFY.get(int(task["sort_order"]))


def verify_task(task, helpers) -> dict:
    """执行验证脚本; PASS 则任务 done + 学习记录闭环。返回结果 dict。"""
    script = _verify_script(task)
    if not script:
        return {"passed": False, "error": "该任务无验证脚本", "output": ""}
    code, out, err = lab_exec(script)
    passed = "PASS" in out and "FAIL" not in out
    output = (out + "\n" + err).strip()
    if not passed:
        return {"passed": False, "output": output or f"exit={code}"}

    # ---- PASS: 闭环 (任务 done + 学习记录 + MD) ----
    now = datetime.date.today().isoformat()
    title = f"Linux Lab 实验：{task['title']}"
    content = (
        f"在 Miglore OS Linux Lab 完成实验「{task['title']}」。\n\n"
        f"实验目标：{task.get('description') or ''}\n\n"
        f"验证结果：PASS（验证脚本：{script[:80]}）\n"
        f"实验环境：隔离容器 {LAB_CONTAINER}（ubuntu:24.04）"
    )
    log_id = helpers["execute_transaction"]([
        (
            "INSERT INTO study_logs (user_id, log_date, task_id, title, content, duration_min, track_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (helpers["USER_ID"], now, task["id"], title, content, 0, LAB_TRACK_ID),
        )
    ])
    if task["status"] != "done":
        helpers["execute"](
            "UPDATE tasks SET status = 'done', completed_at = NOW(), updated_at = NOW() "
            "WHERE id = %s AND user_id = %s",
            (task["id"], helpers["USER_ID"]),
        )
    log = helpers["get_study_log"](log_id) or {}
    filename, path = helpers["generate_markdown"](log, task)
    return {
        "passed": True,
        "task": helpers["get_task"](task["id"]),
        "study_log": {"id": log_id, "title": title, "markdown": filename},
    }


# ========== 路由注册 (由 app.py 调用, 注入 db helpers) ==========

def register(app, helpers: dict) -> None:
    """注册 /api/lab/* 路由; helpers 注入 app 的 db 工具函数。"""

    @app.post("/api/lab/exec")
    def lab_exec_api():
        body = request_body()
        cmd = (body.get("cmd") or "").strip()
        if not cmd:
            return {"error": {"code": "VALIDATION_ERROR", "message": "cmd required"}}, 422
        if not lab_running():
            ok, msg = lab_reset() if body.get("auto_reset") else (False, "Lab 容器未运行, 请点击 Reset")
            if not ok:
                return {"error": {"code": "LAB_DOWN", "message": msg}}, 503
        code, out, err = lab_exec(cmd)
        return {"data": {"exit_code": code, "stdout": out, "stderr": err}}

    @app.post("/api/lab/reset")
    def lab_reset_api():
        ok, msg = lab_reset()
        if not ok:
            return {"error": {"code": "LAB_RESET_FAILED", "message": msg}}, 500
        return {"data": {"ok": True, "message": "Lab 环境已重置"}}

    @app.post("/api/lab/verify")
    def lab_verify_api():
        body = request_body()
        task_id = body.get("task_id")
        if not task_id:
            return {"error": {"code": "VALIDATION_ERROR", "message": "task_id required"}}, 422
        task = helpers["get_task"](int(task_id))
        if not task:
            return {"error": {"code": "NOT_FOUND", "message": "task not found"}}, 404
        if int(task.get("track_id") or 0) != LAB_TRACK_ID:
            return {"error": {"code": "NOT_LAB_TASK", "message": "该任务不属于 Linux Lab"}}, 400
        result = verify_task(task, helpers)
        if "error" in result:
            return {"error": {"code": "VERIFY_UNSUPPORTED", "message": result["error"]}}, 422
        return {"data": result}

    def request_body():
        return request.get_json(silent=True) or {}
