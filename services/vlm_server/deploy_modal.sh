#!/bin/bash
# Deploy script for Gnosis Modal VLM inference app
# Usage: ./deploy_modal.sh [--test]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Gnosis Modal VLM Deployment"
echo "=========================================="

# Check if Modal is installed
if ! command -v modal &> /dev/null; then
    echo "❌ Modal CLI not found. Installing..."
    pip install modal
fi

# Check Modal authentication
echo "Checking Modal authentication..."
if ! modal token show &> /dev/null; then
    echo "❌ Not authenticated with Modal. Run: modal token new"
    exit 1
fi
echo "✅ Modal authenticated"

# Create HuggingFace secret if needed
echo ""
echo "Checking HuggingFace secret..."
if ! modal secret list 2>/dev/null | grep -q "huggingface-secret"; then
    echo "⚠️  HuggingFace secret not found."
    echo "   If you need private models, create it with:"
    echo "   modal secret create huggingface-secret HF_TOKEN=<your-token>"
else
    echo "✅ HuggingFace secret exists"
fi

# Deploy or test
if [[ "$1" == "--test" ]]; then
    echo ""
    echo "Running local test..."
    modal run modal_app.py
else
    echo ""
    echo "Deploying to Modal..."
    modal deploy modal_app.py
    
    echo ""
    echo "=========================================="
    echo "✅ Deployment complete!"
    echo ""
    echo "App name: gnosis-infer-app"
    echo "Class: OCRInference"
    echo ""
    echo "To test:"
    echo "  modal run modal_app.py"
    echo ""
    echo "To view logs:"
    echo "  modal app logs gnosis-infer-app"
    echo "=========================================="
fi
