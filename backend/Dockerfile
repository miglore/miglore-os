# Miglore OS Backend — 开发环境容器镜像
# 仅用于 miglore-os-dev (与生产 /var/www/miglore.fun 完全隔离)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY app.py .

# 非 root 运行 (gunicorn worker)
RUN useradd --create-home appuser \
    && mkdir -p /generated-posts \
    && chown -R appuser:appuser /app /generated-posts

USER appuser

EXPOSE 5001

# 容器内绑定 0.0.0.0 (容器网络隔离); 宿主映射由 compose 限制为 127.0.0.1
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "60", "app:app"]
