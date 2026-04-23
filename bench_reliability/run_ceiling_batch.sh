#!/bin/bash
# Run ceiling baseline for one backend (codex local OR claude SSH+tmux).
# Each invocation runs 10 topics for the given (label, backend) combo.
set -uo pipefail
cd "$(dirname "$0")"

LABEL="${1:?label required (eg gpt-codex / opus-4-7)}"
BACKEND="${2:?backend required (codex / claude)}"
MODEL_ID="${3:-opus}"

LOGS=/tmp/bench_ceiling_${LABEL}_$(date +%Y%m%d-%H%M%S)
mkdir -p "$LOGS"
PYTHON=../.venv/bin/python

notify() { osascript -e "display notification \"$1\" with title \"Ceiling bench\" sound name \"Glass\"" 2>/dev/null || true; }

echo "=== [$(date +%H:%M:%S)] $LABEL ($BACKEND) START ==="
notify "$LABEL ceiling started"

for topic in topics/*.yaml; do
  tid=$(basename "$topic" .yaml)
  echo "--- $tid ---"
  "$PYTHON" ceiling_runner.py \
    --model-label "$LABEL" \
    --backend "$BACKEND" \
    --model-id "$MODEL_ID" \
    --topic "$topic" \
    > "$LOGS/${tid}.log" 2>&1
  rc=$?
  echo "    rc=$rc, $(grep -E 'score|completion' $LOGS/${tid}.log | head -2 | tr -d '\\n,\"')"
done

echo ""
echo "=== [$(date +%H:%M:%S)] $LABEL DONE ==="
notify "$LABEL ceiling done"

"$PYTHON" report.py --model "$LABEL" 2>&1 | head -30 | tee "$LOGS/_summary.txt"
