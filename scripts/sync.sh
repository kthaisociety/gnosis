#!/bin/bash
CURRENT_DIR=$(pwd)
echo $(pwd)

cd lib
uv sync
echo $(pwd)
cd $CURRENT_DIR

cd services/eval
uv sync
echo $(pwd)
cd $CURRENT_DIR

cd services/vlm_server
uv sync
echo $(pwd)
cd $CURRENT_DIR

cd services/gateway
uv sync
echo $(pwd)
cd $CURRENT_DIR

echo "Done (sync)"
