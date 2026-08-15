"""Miglore OS — JD Analyzer (Rule-based, 非 AI)

第一版规则匹配:
1. 从 JD 文本提取技能关键词 (别名归一化)
2. 与个人技能库 (skills 表) 比较
3. 输出 MATCH / PARTIAL / MISSING + JD Match Score

明确不声称 AI 智能匹配。
"""

# 关键词 → 标准技能名 (复合词在前, 避免短词先匹配)
SKILL_ALIASES: dict[str, str] = {
    "docker compose": "Docker",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "shell": "Shell",
    "bash": "Shell",
    "python": "Python",
    "docker": "Docker",
    "nginx": "Nginx",
    "mysql": "MySQL",
    "redis": "Redis",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "git": "Git",
    "github": "Git",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "ansible": "Ansible",
    "云计算": "云计算",
    "aws": "云计算",
    "腾讯云": "云计算",
    "阿里云": "云计算",
    "systemd": "systemd",
}

# 技能库状态 → 匹配档位
# MATCH: learned (已掌握)  |  PARTIAL: learning (已学未完成)  |  MISSING: 不在库/idle


def extract_skills(text: str) -> list[str]:
    """从文本提取技能关键词 (去重, 保持出现顺序)。"""
    lowered = text.lower()
    found: list[str] = []
    for alias, canonical in SKILL_ALIASES.items():
        if alias in lowered and canonical not in found:
            found.append(canonical)
    return found


def analyze_jd(jd_text: str, user_skills: list[dict]) -> dict:
    """规则匹配: 需求技能 vs 个人技能库。"""
    required = extract_skills(jd_text)
    skill_map = {s["name"]: s for s in user_skills}

    matched: list[str] = []
    partial: list[str] = []
    missing: list[str] = []
    for name in required:
        sk = skill_map.get(name)
        if sk and sk.get("status") == "learned":
            matched.append(name)
        elif sk and sk.get("status") == "learning":
            partial.append(name)
        else:
            missing.append(name)

    total = len(required)
    score = round(len(matched) / total * 100) if total else 0
    return {
        "engine": "rule-based",
        "total_required": total,
        "required": required,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "score": score,
    }
