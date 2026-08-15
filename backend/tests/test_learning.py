"""learning 接口测试"""


def test_learning_shape(client):
    resp = client.get("/api/learning")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert set(data.keys()) == {"tracks", "current", "progress", "tasks"}
    assert data["tracks"], "应有 seed 路线"
    assert data["current"]["title"] == "测试路线"


def test_learning_progress(client):
    resp = client.get("/api/learning")
    data = resp.get_json()["data"]
    # 3 个任务, 1 done → 33%
    assert data["progress"] == {"done": 1, "total": 3, "percent": 33}
    assert data["current"]["progress"] == 33


def test_learning_tasks_join(client):
    resp = client.get("/api/learning")
    tasks = resp.get_json()["data"]["tasks"]
    assert len(tasks) == 3
    for t in tasks:
        assert t["track_name"] == "测试路线"
        assert t["skill_name"] == "Linux"
