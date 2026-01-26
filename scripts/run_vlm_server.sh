#!/bin/bash
# Run the inference server
cd services/vlm_server
uv run python -m vlm_server.server
cd ../..
