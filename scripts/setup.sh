#!/bin/bash
set -e

# Change to the script's directory to ensure paths are correct
cd "$(dirname "$0")/.."

echo "Installing/updating workspace packages in editable mode..."
uv pip install -e lib services/gateway services/vlm_server

echo "Setup complete. You can now run the services using:"
echo "uv run gateway-server"
echo "uv run vlm-server"
