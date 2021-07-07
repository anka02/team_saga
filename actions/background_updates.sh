#!/usr/bin/env bash
set -e
THIS_DIR=$( cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

NLG_DIR=$THIS_DIR/../nlg
echo "Running $0 in $NLG_DIR"
python "$NLG_DIR/run_background_updates.py" &