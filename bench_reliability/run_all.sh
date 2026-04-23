#!/bin/bash
# Run all topics for a single (model_label, endpoint, model_id) triple.
# Usage:
#   ./run_all.sh 27b-6bit  http://127.0.0.1:8820/v1  mlx-community/Qwen3.6-27B-6bit
#   ./run_all.sh 35b-a3b   http://127.0.0.1:8810/v1  qwen3.6-q8kxl
#   ./run_all.sh opus-4-7  http://127.0.0.1:4000/v1  claude-opus-4-7
set -euo pipefail
cd "$(dirname "$0")"

MODEL_LABEL="${1:?model label required}"
ENDPOINT="${2:?endpoint required}"
MODEL_ID="${3:?model id required}"
API_KEY="${4:-bench}"

PYTHON="../.venv/bin/python"

echo "=== Running 10 topics on $MODEL_LABEL ==="
echo "    endpoint: $ENDPOINT"
echo "    model_id: $MODEL_ID"
echo ""

for topic in topics/*.yaml; do
  echo "--- $(basename $topic .yaml) ---"
  "$PYTHON" runner.py \
    --model-label "$MODEL_LABEL" \
    --endpoint "$ENDPOINT" \
    --model-id "$MODEL_ID" \
    --topic "$topic" \
    --api-key "$API_KEY" \
    2>&1 | tail -25
  echo ""
done

echo "=== DONE — running report ==="
"$PYTHON" report.py --model "$MODEL_LABEL"
