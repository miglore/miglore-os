"""Linux Lab API 测试 (mock docker 操作, 不碰真实容器)"""

from unittest import mock

import app as app_module


def _mock_exec(stdout="", stderr="", code=0):
    return mock.patch("lab.lab_exec", return_value=(code, stdout, stderr))


def test_lab_exec_requires_cmd(client):
    r = client.post("/api/lab/exec", json={})
    assert r.status_code == 422


def test_lab_exec_ok(client):
    with mock.patch("lab.lab_running", return_value=True), _mock_exec(stdout="Linux miglab 6.8.0\n", code=0):
        r = client.post("/api/lab/exec", json={"cmd": "uname -a"})
    assert r.status_code == 200
    d = r.get_json()["data"]
    assert d["exit_code"] == 0
    assert "Linux miglab" in d["stdout"]


def test_lab_exec_container_down(client):
    with mock.patch("lab.lab_running", return_value=False), mock.patch("lab.lab_reset", return_value=(False, "down")):
        r = client.post("/api/lab/exec", json={"cmd": "ls"})
    assert r.status_code == 503


def test_lab_reset_ok(client):
    with mock.patch("lab.lab_running", return_value=True), mock.patch("lab.lab_exec", return_value=(0, "LAB_RESET_OK", "")):
        r = client.post("/api/lab/reset")
    assert r.status_code == 200
    assert r.get_json()["data"]["ok"] is True


def test_lab_verify_not_lab_task(client):
    r = client.post("/api/lab/verify", json={"task_id": 1})  # track 1 任务
    assert r.status_code == 400
    assert r.get_json()["error"]["code"] == "NOT_LAB_TASK"


def test_lab_verify_unknown_task(client):
    r = client.post("/api/lab/verify", json={"task_id": 99999})
    assert r.status_code == 404


def test_lab_verify_pass_completes_task_and_log(client):
    # task 101 = '05 mkdir' (sort_order=5, track=2), mock 验证 PASS
    with mock.patch("lab.lab_running", return_value=True), _mock_exec(stdout="PASS\n", code=0):
        r = client.post("/api/lab/verify", json={"task_id": 101})
    assert r.status_code == 200
    d = r.get_json()["data"]
    assert d["passed"] is True
    assert d["task"]["status"] == "done"
    assert d["study_log"]["id"] > 0

    # 验证闭环: 任务 done + 学习记录存在 + MD 生成
    with app_module.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM tasks WHERE id = 101")
        assert cur.fetchone()["status"] == "done"
        cur.execute("SELECT COUNT(*) c FROM study_logs WHERE task_id = 101")
        assert cur.fetchone()["c"] == 1


def test_lab_verify_fail_keeps_task(client):
    with mock.patch("lab.lab_running", return_value=True), _mock_exec(stdout="FAIL: 请先执行 mkdir -p /tmp/miglab\n", code=1):
        r = client.post("/api/lab/verify", json={"task_id": 101})
    assert r.status_code == 200
    assert r.get_json()["data"]["passed"] is False
    with app_module.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM tasks WHERE id = 101")
        assert cur.fetchone()["status"] == "todo"
        cur.execute("SELECT COUNT(*) c FROM study_logs WHERE task_id = 101")
        assert cur.fetchone()["c"] == 0
