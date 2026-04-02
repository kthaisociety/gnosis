FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Create directory structure for workspace
RUN mkdir -p lib/src/lib services/gateway/src/gateway services/vlm_server/src/vlm_server

# Copy the lock file and pyproject.toml files
COPY uv.lock .
COPY pyproject.toml .
COPY lib/pyproject.toml lib/
COPY services/gateway/pyproject.toml services/gateway/
COPY services/vlm_server/pyproject.toml services/vlm_server/

# Create placeholder __init__.py files for uv sync to work
RUN touch lib/src/lib/__init__.py services/gateway/src/gateway/__init__.py services/vlm_server/src/vlm_server/__init__.py

# Install dependencies from the lock file for gateway and lib
RUN uv sync --frozen --no-install-project --package gateway --package lib

# Copy the rest of the project, respecting .dockerignore
COPY . .

# Install the project packages
RUN uv sync --frozen --package gateway --package lib

# Expose the gateway port
EXPOSE 8000

# Command to run the gateway server
CMD ["uv", "run", "gateway-server"]
