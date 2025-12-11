# syntax=docker/dockerfile:1
FROM python:3.13-slim

# System dependencies for OpenCV (opencv-python wheel)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libgl1 \
       libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

# Expected runtime env (provided by platform/.env):
# - GRPC_PORT (default handled by app: 50051)
# - LOGGING_LEVEL (INFO/DEBUG/etc.)

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["python", "-u", "src/server.py"]

