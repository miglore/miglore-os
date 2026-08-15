"""study-logs 接口测试 (含 Markdown 生成)"""


def test_create_study_log(client, md_tmp):
    resp = client.post("/api/study-logs", json={
        "task_id": 2,
        "content": "今天学习了 systemd 的 MainPID 守护关系。",
    })
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["log"]["title"] == "测试任务B"
    assert data["log"]["task_id"] == 2
    assert data["task"]["status"] == "done", "保存日志应自动完成任务"
    assert data["markdown"]["filename"].endswith(".md")
    # MD 文件真实生成
    assert (md_tmp / data["markdown"]["filename"]).exists()


def test_create_study_log_requires_content(client):
    resp = client.post("/api/study-logs", json={"task_id": 2})
    assert resp.status_code == 422


def test_create_study_log_unknown_task(client):
    resp = client.post("/api/study-logs", json={"task_id": 9999, "content": "x"})
    assert resp.status_code == 404


def test_list_study_logs(client, md_tmp):
    client.post("/api/study-logs", json={"task_id": 1, "content": "任务A记录"})
    resp = client.get("/api/study-logs")
    logs = resp.get_json()["data"]["logs"]
    assert len(logs) == 1
    assert logs[0]["task_title"] == "测试任务A"


def test_get_study_log(client, md_tmp):
    client.post("/api/study-logs", json={"task_id": 1, "content": "任务A记录"})
    resp = client.get("/api/study-logs/1")
    log = resp.get_json()["data"]["log"]
    assert log["id"] == 1
    assert log["content"] == "任务A记录"


def test_get_study_log_not_found(client):
    resp = client.get("/api/study-logs/9999")
    assert resp.status_code == 404


def test_patch_study_log(client, md_tmp):
    client.post("/api/study-logs", json={"task_id": 1, "content": "原始内容"})
    resp = client.patch("/api/study-logs/1", json={"duration_min": 60, "mood": 4})
    assert resp.status_code == 200
    log = resp.get_json()["data"]["log"]
    assert log["duration_min"] == 60
    assert log["mood"] == 4


def test_markdown_content(client, md_tmp):
    client.post("/api/study-logs", json={
        "task_id": 1,
        "content": "今天学习了 systemd、Gunicorn master/worker 以及 systemd 对 MainPID 的守护关系。",
    })
    md_file = list(md_tmp.glob("*.md"))[0]
    text = md_file.read_text(encoding="utf-8")
    assert "title: \"测试任务A\"" in text
    assert "categories:" in text and "- 学习" in text
    assert "## 今天学到了什么" in text
    assert "MainPID" in text
    assert "## 相关任务" in text
