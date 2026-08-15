"""metrics 接口测试 (prometheus-client)"""


def test_metrics_endpoint(client):
    # 先发两个请求产生计数
    client.get("/api/health")
    client.get("/api/learning")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text
    assert "process_start_time_seconds" in text
    # health 请求已计数 (method GET)
    assert 'http_requests_total{method="GET",path="/api/health",status="200"}' in text


def test_metrics_content_type(client):
    resp = client.get("/metrics")
    assert resp.content_type.startswith("text/plain")
