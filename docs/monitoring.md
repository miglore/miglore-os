# Miglore OS — 监控设计 (Prometheus + Grafana)

> 阶段：V1 第五阶段 | 环境：miglore-os-dev 开发环境 | 与生产完全隔离

## 1. 基础概念

### Prometheus 是什么
开源的时序数据库 + 监控系统。周期性地向目标服务发起 HTTP 抓取（scrape），拉取指标（metrics）并按时间存储，支持 PromQL 查询与告警。由 Prometheus Server、targets（被监控对象）、TSDB（时序存储）组成。

### Grafana 是什么
可视化分析平台。连接 Prometheus 等数据源，把时序指标渲染成图表/仪表盘，支持告警通知。Grafana **不采集数据**，只查询展示。

### Exporter 是什么
把第三方系统的内部状态转换成 Prometheus 指标格式的代理进程。例如 node_exporter 暴露主机 CPU/内存/磁盘指标、mysqld_exporter 暴露 MySQL 指标、业务服务自身也可暴露指标（本项目的 backend 即通过 prometheus-client 直接暴露 /metrics，无需额外 exporter）。

### Pull 模型是什么
Prometheus 主动去 **拉**（pull）目标暴露的 /metrics 端点，而不是目标主动**推**（push）数据。好处：采集频率可控、目标无状态、单点故障面小。对应 prometheus.yml 的 `scrape_configs`。

### Prometheus 如何发现 targets
静态发现：在 prometheus.yml 里写死 target 地址（`static_configs`，本阶段使用）；动态发现：基于 DNS/consul/K8s 等自动发现（后续阶段可引入）。

### metrics / labels 概念
- **metric**：一个带名称的时序量，如 `http_requests_total`。类型：Counter（只增计数）、Gauge（可增可减）、Histogram（分布采样，_bucket/_sum/_count）、Summary。
- **labels**：指标的维度标签，如 `method="GET", path="/api/health", status="200"`。同一 metric 名称 + 不同标签组合 = 不同时间序列。查询时可按标签聚合（`by (path)`）。

## 2. 当前监控架构

```
┌────────────┐  scrape  ┌─────────────────┐
│ Prometheus │─────────▶│ backend:5001     │  /metrics (prometheus-client)
│ :9090      │          │  http_requests_total / latency histogram
│ (127.0.0.1)│          └─────────────────┘
│            │  scrape  ┌─────────────────┐
│            │─────────▶│ prometheus:9090  │  自身指标 (go/metrics)
│            │          └─────────────────┘
└─────┬──────┘
      │ datasource (provisioning)
┌─────▼──────┐
│  Grafana   │  127.0.0.1:3000 (开发专用账号, provisioning 自动配置)
│  :3000     │  Miglore OS Overview dashboard
└────────────┘
```

### 范围决策（明确报告）

- **监控对象**：Prometheus 自身 + Miglore OS backend（开发环境容器内）。
- **Node Exporter 不做**：node_exporter 需挂载宿主机 `/proc` `/sys` `/rootfs` 读取**宿主机**指标。按阶段要求「不要把宿主机 /proc /sys /rootfs 暴露进容器；需要额外权限就先不做」——本阶段不实现宿主机 exporter，**不绕过安全限制**。后续如需主机监控，另行评估（只读挂载 + 专用用户）。
- **容器内部指标**：backend 与 prometheus 均为容器网络内服务，通过 compose 服务名直接 scrape，天然隔离。
- 所有服务仅绑定 127.0.0.1，无公网暴露。

## 3. Backend 指标设计

| 指标 | 类型 | 标签 | 说明 |
|---|---|---|---|
| `http_requests_total` | Counter | method, path, status | 累计请求数 |
| `http_request_duration_seconds` | Histogram | method, path | 请求耗时（bucket 分布） |
| `process_start_time_seconds` | Gauge | — | 进程启动时间（uptime 计算用） |
| `backend_up` | Gauge | — | 1=存活（Grafana up 面板辅助） |

path 标签使用 Flask `url_rule`（模板路径，如 `/api/tasks/<int:task_id>`），避免高基数。

## 4. Grafana 设计

- **数据源**：Prometheus（url `http://prometheus:9090`，容器网络），通过 provisioning 自动注册（声明式，重启不丢失）。
- **Dashboard**：`Miglore OS Overview`，含 5 面板：
  1. Backend request rate：`sum(rate(http_requests_total{job="backend"}[5m])) by (path)`
  2. Backend request latency：`histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="backend"}[5m])) by (le))`
  3. Backend error rate：`sum(rate(http_requests_total{job="backend", status=~"5.."}[5m]))`
  4. Backend uptime：`time() - process_start_time_seconds{job="backend"}`
  5. Prometheus target status：`up`
- 登录：开发专用账号（admin + 随机密码，写入 compose .env，不入库）。
