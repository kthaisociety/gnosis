#!/bin/bash
# Setup script for Gnosis
bash scripts/sync.sh
bash scripts/gen_grpc_protos.sh

echo "Done (setup)"
