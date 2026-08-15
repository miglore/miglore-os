"""Career API 测试: 方向/投递/面试 CRUD + 聚合"""


def _mk_direction(client, name="DevOps/运维开发"):
    r = client.post("/api/career/directions", json={"name": name, "target_role": "DevOps 工程师"})
    assert r.status_code == 201
    return r.get_json()["data"]["direction"]["id"]


def _mk_application(client, direction_id, status="applied"):
    r = client.post("/api/applications", json={
        "direction_id": direction_id, "company": "某某云", "position": "运维工程师",
        "city": "上海", "salary": "15-20K", "status": status,
    })
    assert r.status_code == 201
    return r.get_json()["data"]["application"]["id"]


def test_direction_crud(client):
    did = _mk_direction(client)
    # list
    r = client.get("/api/career/directions")
    assert len(r.get_json()["data"]["directions"]) == 1
    # patch status
    r = client.patch(f"/api/career/directions/{did}", json={"status": "paused"})
    assert r.get_json()["data"]["direction"]["status"] == "paused"
    # delete
    r = client.delete(f"/api/career/directions/{did}")
    assert r.get_json()["data"]["deleted"] is True
    assert client.get("/api/career/directions").get_json()["data"]["directions"] == []


def test_direction_requires_name(client):
    r = client.post("/api/career/directions", json={})
    assert r.status_code == 422


def test_application_crud_with_city_salary(client):
    did = _mk_direction(client)
    r = client.post("/api/applications", json={
        "direction_id": did, "company": "某某云", "position": "运维工程师",
        "city": "上海", "salary": "15-20K", "channel": "BOSS直聘", "status": "interviewing",
    })
    assert r.status_code == 201
    app = r.get_json()["data"]["application"]
    assert app["city"] == "上海"
    assert app["salary"] == "15-20K"
    assert app["direction_name"] == "DevOps/运维开发"
    aid = app["id"]
    # 状态流转
    r = client.patch(f"/api/applications/{aid}", json={"status": "offer"})
    assert r.get_json()["data"]["application"]["status"] == "offer"
    # 过滤
    r = client.get("/api/applications?status=offer")
    assert len(r.get_json()["data"]["applications"]) == 1
    # delete
    assert client.delete(f"/api/applications/{aid}").get_json()["data"]["deleted"] is True


def test_application_requires_company_position(client):
    r = client.post("/api/applications", json={"company": "X"})
    assert r.status_code == 422


def test_interview_crud(client):
    did = _mk_direction(client)
    aid = _mk_application(client, did, status="interviewing")
    r = client.post("/api/interviews", json={
        "application_id": aid, "round": "一面", "scheduled_at": "2026-08-20 10:00:00",
    })
    assert r.status_code == 201
    ivw = r.get_json()["data"]["interview"]
    assert ivw["company"] == "某某云"
    assert ivw["position"] == "运维工程师"
    iid = ivw["id"]
    # 结果更新
    r = client.patch(f"/api/interviews/{iid}", json={"result": "passed", "review": "基础扎实"})
    d = r.get_json()["data"]["interview"]
    assert d["result"] == "passed"
    assert d["review"] == "基础扎实"
    # delete
    assert client.delete(f"/api/interviews/{iid}").get_json()["data"]["deleted"] is True


def test_interview_requires_valid_application(client):
    r = client.post("/api/interviews", json={"application_id": 9999})
    assert r.status_code == 404


def test_career_aggregate(client):
    did = _mk_direction(client)
    _mk_application(client, did, status="applied")
    aid2 = _mk_application(client, did, status="interviewing")
    _mk_application(client, did, status="rejected")
    client.post("/api/interviews", json={
        "application_id": aid2, "round": "二面", "scheduled_at": "2026-08-20 14:00:00",
    })
    r = client.get("/api/career")
    d = r.get_json()["data"]
    assert len(d["directions"]) == 1
    assert d["directions"][0]["application_count"] == 3
    s = d["stats"]
    assert s["total"] == 3
    assert s["interviewing"] == 1
    assert s["rejected"] == 1
    assert s["pending_interviews"] == 1
    assert len(d["recent_applications"]) == 3
    assert len(d["upcoming_interviews"]) == 1
