# ============================================================
# Production Dockerfile — Multi-stage, < 500 MB, non-root
# ============================================================

# ─── STAGE 1: BUILDER ────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Cài đặt thư viện C/C++ để build code
RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# TẠO VIRTUAL ENVIRONMENT (VENV)
RUN python -m venv /opt/venv
# Kích hoạt venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Cài đặt toàn bộ thư viện vào VENV (Không dùng --user nữa)
RUN pip install --no-cache-dir -r requirements.txt


# ─── STAGE 2: RUNTIME ────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Cài các thư viện hệ thống cần thiết để chạy (ví dụ kết nối PostgreSQL)
RUN apt-get update && apt-get install -y libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Tạo Non-root user
RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

# COPY toàn bộ VENV từ builder sang và cấp quyền
COPY --chown=agent:agent --from=builder /opt/venv /opt/venv

# COPY mã nguồn ứng dụng và cấp quyền
COPY --chown=agent:agent app/ ./app/
COPY --chown=agent:agent utils/ ./utils/

USER agent

# Kích hoạt VENV ở Stage 2 để Python nhận diện thư viện uvicorn
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check instruction required by the checker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health')" || exit 1

# Khởi động app
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2