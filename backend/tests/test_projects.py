"""Projects + Evidence + Interview Evidence API 测试"""


def _mk_evidence(client, pid=1, title="测试证据", category="docker"):
    r = client.post(f"/api/projects/{pid}/evidence", json={
        "title": title, "category": category,
        "description": "做了什么", "technical_detail": "技术细节", "result": "结果",
    })
    assert r.status_code == 201
    return r.get_json()["data"]["evidence"]["id"]


# ---- Projects ----

def test_project_list_with_stats(client):
    r = client.get("/api/projects")
    assert r.status_code == 200
    d = r.get_json()["data"]
    assert len(d["projects"]) == 1
    assert d["projects"][0]["name"] == "测试项目"
    assert d["stats"]["total"] == 1
    assert d["stats"]["tech_stacks"] >= 1


def test_project_detail(client):
    r = client.get("/api/projects/1")
    d = r.get_json()["data"]
    assert d["project"]["tech_stack"] == "Svelte·Flask·Docker"
    assert d["milestones"] == []
    assert d["evidence"] == []


def test_project_detail_not_found(client):
    r = client.get("/api/projects/9999")
    assert r.status_code == 404


# ---- Evidence CRUD ----

def test_evidence_crud(client):
    eid = _mk_evidence(client)
    # list
    r = client.get("/api/projects/1/evidence")
    evs = r.get_json()["data"]["evidence"]
    assert len(evs) == 1
    assert evs[0]["category"] == "docker"
    # patch
    r = client.patch(f"/api/evidence/{eid}", json={"category": "ci_cd", "result": "更新结果"})
    e = r.get_json()["data"]["evidence"]
    assert e["category"] == "ci_cd"
    assert e["result"] == "更新结果"
    # delete
    assert client.delete(f"/api/evidence/{eid}").get_json()["data"]["deleted"] is True
    assert client.get("/api/projects/1/evidence").get_json()["data"]["evidence"] == []


def test_evidence_invalid_category(client):
    r = client.post("/api/projects/1/evidence", json={"title": "x", "category": "hack"})
    assert r.status_code == 422


def test_evidence_requires_title(client):
    r = client.post("/api/projects/1/evidence", json={"category": "docker"})
    assert r.status_code == 422


def test_evidence_unknown_project(client):
    r = client.post("/api/projects/9999/evidence", json={"title": "x"})
    assert r.status_code == 404


# ---- Interview Evidence ----

def test_interview_evidence_crud_with_skill(client):
    eid = _mk_evidence(client, title="Docker 容器化")
    # skill_id=5 是 conftest seed 的 Docker 技能? 不 — conftest skills 只有 Linux(id=1)
    r = client.post(f"/api/evidence/{eid}/interview", json={
        "question": "你 Docker 用到什么程度？",
        "answer": "multi-stage 构建、非 root 运行、compose 编排、healthcheck。",
        "skill_id": 1,  # Linux 技能 (conftest seed)
    })
    assert r.status_code == 201
    ivw = r.get_json()["data"]["interview"]
    assert ivw["evidence_id"] == eid
    assert ivw["skill_name"] == "Linux"
    assert ivw["project_id"] == 1
    # list
    r = client.get(f"/api/evidence/{eid}/interview")
    ivws = r.get_json()["data"]["interviews"]
    assert len(ivws) == 1
    assert ivws[0]["answer"].startswith("multi-stage")


def test_interview_requires_question_answer(client):
    eid = _mk_evidence(client)
    r = client.post(f"/api/evidence/{eid}/interview", json={"question": "只有问题"})
    assert r.status_code == 422


def test_interview_unknown_skill(client):
    eid = _mk_evidence(client)
    r = client.post(f"/api/evidence/{eid}/interview", json={
        "question": "q", "answer": "a", "skill_id": 9999,
    })
    assert r.status_code == 404


def test_interview_unknown_evidence(client):
    r = client.post("/api/evidence/9999/interview", json={"question": "q", "answer": "a"})
    assert r.status_code == 404
