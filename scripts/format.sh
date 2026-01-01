#!/bin/bash
# Format using Ruff
set -e

echo "Formatting (ruff) --fix..."
uvx ruff check --fix .

echo "Formatting (Ruff)..."
uvx ruff format .

echo "Done"