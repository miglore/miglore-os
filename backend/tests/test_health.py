"""health 接口测试"""


def test_health_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_health_shape(client):
    resp = client.get("/api/health")
    body = resp.get_json()
    assert set(body.keys()) == {"data"}
    assert set(body["data"].keys()) == {"status", "service", "database", "time"}
