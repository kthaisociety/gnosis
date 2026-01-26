#!/bin/bash
# Run the Gateway server
cd services/gateway
uv run python -m gateway.server
cd ../..
