#!/bin/bash
# Follow-up batch: vanilla 35B-A3B-4bit-DWQ → 27B mxfp8 → 27B mxfp4.
# Runs after main 3-model batch finishes. DWQ uses :8811 sidekick (no swap needed),
# mxfp8/mxfp4 swap on :8820.
set -uo pipefail
cd "$(dirname "$0")"

LOGS=/tmp/bench_reliability_followup_$(date +%Y%m%d-%H%M%S)
mkdir -p "$LOGS"
echo "Logs: $LOGS"

notify() {
  osascript -e "display notification \"$1\" with title \"Reliability bench\" sound name \"Glass\"" 2>/dev/null || true
}

run_model() {
  local label="$1" endpoint="$2" model_id="$3"
  local logfile="$LOGS/${label}.log"
  echo "=== [$(date +%H:%M:%S)] $label START ==="
  notify "$label batch started"
  ./run_all.sh "$label" "$endpoint" "$model_id" > "$logfile" 2>&1
  local rc=$?
  echo "=== [$(date +%H:%M:%S)] $label DONE (rc=$rc) ==="
  notify "$label batch done"
  return $rc
}

swap_8820_to() {
  local model_id="$1"
  local label="$2"
  echo "=== [$(date +%H:%M:%S)] Swapping :8820 → $label ==="
  PID_OLD=$(lsof -tiTCP:8820 -sTCP:LISTEN 2>/dev/null | head -1)
  [ -n "$PID_OLD" ] && kill "$PID_OLD" && sleep 5
  nohup /Users/fran/projects/qwen-mlx-bench/.venv/bin/mlx_lm.server \
    --model "$model_id" --host 127.0.0.1 --port 8820 \
    > "/tmp/mlx-${label}.log" 2>&1 &
  echo "$label server PID=$!"
  for i in {1..20}; do
    sleep 8
    curl -s -m 3 http://127.0.0.1:8820/v1/models 2>&1 | grep -q "$(echo $model_id | rev | cut -d/ -f1 | rev)" && { echo "✅ $label warm"; return 0; }
  done
  echo "⚠️ $label warm timeout"
  return 1
}

# 1. vanilla 35B-A3B-DWQ on :8811 (sidekick, already running per memory)
# Check if it's actually serving
DWQ_OK=$(curl -s -m 3 http://127.0.0.1:8811/v1/models 2>&1 | grep -c "Qwen3.6-35B-A3B-4bit-DWQ" || true)
if [ "$DWQ_OK" -gt 0 ]; then
  run_model "35b-a3b-dwq-vanilla" "http://127.0.0.1:8811/v1" "mlx-community/Qwen3.6-35B-A3B-4bit-DWQ"
else
  echo "⚠️ DWQ sidekick :8811 not serving — skipping DWQ"
fi

# 2. 27B mxfp8 on :8820 (swap from current 8bit)
swap_8820_to "mlx-community/Qwen3.6-27B-mxfp8" "27b-mxfp8"
run_model "27b-mxfp8" "http://127.0.0.1:8820/v1" "mlx-community/Qwen3.6-27B-mxfp8"

# 3. 27B mxfp4 on :8820 (swap)
swap_8820_to "mlx-community/Qwen3.6-27B-mxfp4" "27b-mxfp4"
run_model "27b-mxfp4" "http://127.0.0.1:8820/v1" "mlx-community/Qwen3.6-27B-mxfp4"

# 4. Final report
echo ""
echo "=== FINAL FOLLOW-UP REPORT ==="
/Users/fran/projects/qwen-mlx-bench/.venv/bin/python report.py 2>&1 | tee "$LOGS/_final_report.txt"

notify "Follow-up batch (DWQ + mxfp8 + mxfp4) ALL DONE"
echo ""
echo "All logs in: $LOGS"
