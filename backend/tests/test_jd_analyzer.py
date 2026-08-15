"""JD Analyzer 测试 (rule-based, 非 AI)"""

from jd_analyzer import analyze_jd, extract_skills


# ---- 关键词提取 ----

def test_extract_skills_basic():
    assert extract_skills("熟悉 Linux 和 Docker Compose，使用 Kubernetes 部署") == [
        "Docker", "Linux", "Kubernetes",
    ]


def test_extract_skills_alias():
    # k8s → Kubernetes
    assert "Kubernetes" in extract_skills("K8s 运维")
    # CI/CD 与 cicd 归一
    assert extract_skills("CI/CD 与 cicd 流程") == ["CI/CD"]
    # 大小写不敏感
    assert extract_skills("python + PYTHON") == ["Python"]


def test_extract_skills_aws_cloud():
    assert extract_skills("熟悉 AWS 与腾讯云") == ["云计算"]


def test_extract_skills_empty():
    assert extract_skills("") == []
    assert extract_skills("团队协作能力强") == []


# ---- 匹配 ----

def test_analyze_match_partial_missing():
    skills = [
        {"name": "Docker", "status": "learned", "level": 4},
        {"name": "Linux", "status": "learning", "level": 3},
    ]
    r = analyze_jd("需要 Docker、Linux、Redis 技能", skills)
    assert r["engine"] == "rule-based"
    assert r["matched"] == ["Docker"]
    assert r["partial"] == ["Linux"]
    assert r["missing"] == ["Redis"]
    assert r["total_required"] == 3
    assert r["score"] == 33  # 1/3 四舍五入


def test_analyze_full_match():
    skills = [{"name": "Docker", "status": "learned"}, {"name": "Linux", "status": "learned"}]
    r = analyze_jd("Docker Linux", skills)
    assert r["score"] == 100
    assert r["missing"] == []


def test_analyze_idle_is_missing():
    skills = [{"name": "Docker", "status": "idle"}]
    r = analyze_jd("需要 Docker", skills)
    assert r["missing"] == ["Docker"]
    assert r["score"] == 0


def test_analyze_empty_jd():
    r = analyze_jd("", [])
    assert r["score"] == 0
    assert r["total_required"] == 0


# ---- API ----

def test_api_jd_analyze(client):
    # conftest seed: skills 表含 Linux (status learning)
    r = client.post("/api/jd-analyze", json={"title": "DevOps 工程师", "jd_text": "熟悉 Linux、Docker、Redis"})
    assert r.status_code == 200
    d = r.get_json()["data"]
    assert d["engine"] == "rule-based"
    assert "Linux" in d["partial"]  # learning → PARTIAL
    assert "Redis" in d["missing"]


def test_api_jd_analyze_requires_text(client):
    r = client.post("/api/jd-analyze", json={"title": "x"})
    assert r.status_code == 422
