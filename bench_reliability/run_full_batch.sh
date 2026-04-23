#!/bin/bash
# Full batch: 27B-6bit (already warm on :8820) → 35B-A3B (英克 :8810) → swap to 27B-8bit on :8820.
# Runs sequentially to avoid Metal GPU contention. Each model logs to its own file.
set -uo pipefail
cd "$(dirname "$0")"

LOGS=/tmp/bench_reliability_$(date +%Y%m%d-%H%M%S)
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

# 1. 27B 6bit on :8820 (already warm)
run_model "27b-6bit" "http://127.0.0.1:8820/v1" "mlx-community/Qwen3.6-27B-6bit"

# 2. 35B-A3B Q8_K_XL on :8810 (英克)
run_model "35b-a3b-q8kxl" "http://127.0.0.1:8810/v1" "qwen3.6-q8kxl"

# 3. Swap 6bit → 8bit on :8820
echo "=== [$(date +%H:%M:%S)] Swapping 6bit → 8bit on :8820 ==="
PID_6BIT=$(lsof -tiTCP:8820 -sTCP:LISTEN 2>/dev/null | head -1)
[ -n "$PID_6BIT" ] && kill "$PID_6BIT" && sleep 5
nohup /Users/fran/projects/qwen-mlx-bench/.venv/bin/mlx_lm.server \
  --model mlx-community/Qwen3.6-27B-8bit \
  --host 127.0.0.1 --port 8820 \
  > /tmp/mlx-27b-8bit.log 2>&1 &
echo "8bit server PID=$!"
# wait for warm
for i in {1..15}; do
  sleep 8
  curl -s -m 3 http://127.0.0.1:8820/v1/models 2>&1 | grep -q "27B-8bit" && { echo "✅ 8bit warm"; break; }
done

run_model "27b-8bit" "http://127.0.0.1:8820/v1" "mlx-community/Qwen3.6-27B-8bit"

# 4. Final report across all 3 models
echo ""
echo "=== FINAL REPORT ==="
/Users/fran/projects/qwen-mlx-bench/.venv/bin/python report.py 2>&1 | tee "$LOGS/_final_report.txt"

notify "ALL 3 batches complete"
echo ""
echo "All logs in: $LOGS"
