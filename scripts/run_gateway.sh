#!/bin/bash
cd services/gateway
uv run python -m gateway.server
cd ../..
