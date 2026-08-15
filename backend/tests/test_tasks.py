"""tasks 接口测试"""


def test_tasks_list(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    tasks = resp.get_json()["data"]["tasks"]
    assert len(tasks) == 3


def test_tasks_filter_status(client):
    resp = client.get("/api/tasks?status=in_progress")
    tasks = resp.get_json()["data"]["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == 2
    assert tasks[0]["title"] == "测试任务B"


def test_tasks_filter_type_limit(client):
    resp = client.get("/api/tasks?type=learning&limit=2")
    tasks = resp.get_json()["data"]["tasks"]
    assert len(tasks) == 2


def test_create_task(client):
    resp = client.post("/api/tasks", json={"type": "learning", "title": "新建任务"})
    assert resp.status_code == 201
    task = resp.get_json()["data"]["task"]
    assert task["title"] == "新建任务"
    assert task["status"] == "todo"


def test_create_task_requires_title(client):
    resp = client.post("/api/tasks", json={"type": "learning"})
    assert resp.status_code == 422


def test_patch_task_done(client):
    resp = client.patch("/api/tasks/2", json={"status": "done"})
    assert resp.status_code == 200
    task = resp.get_json()["data"]["task"]
    assert task["status"] == "done"
    assert task["completed_at"] is not None


def test_patch_task_invalid_status(client):
    resp = client.patch("/api/tasks/2", json={"status": "hacked"})
    assert resp.status_code == 422


def test_patch_task_not_found(client):
    resp = client.patch("/api/tasks/9999", json={"status": "done"})
    assert resp.status_code == 404
