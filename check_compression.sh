#!/usr/bin/env bash
# Compression trigger telemetry — scans Hermes coder agent.log, shows:
# - trigger time + compressed via which model endpoint
# - context size at trigger (from nearest preceding API call)
# - any failures
#
# Usage: ./check_compression.sh [days]   (default: 7)
#
# NOTE: Q8_K_XL stack landed 2026-04-17. Anything BEFORE that is stale
# data from the old oMLX Qwen3-Coder-Next-4bit compression backend and
# is NOT comparable to current setup. Script floors SINCE to 2026-04-17
# automatically to avoid this pitfall.

set -euo pipefail

LOG=~/.hermes/profiles/coder/logs/agent.log
DAYS="${1:-7}"
STACK_START="2026-04-17"

if [[ ! -f "$LOG" ]]; then
    echo "no agent log at $LOG"
    exit 1
fi

SINCE=$(date -v-${DAYS}d +%Y-%m-%d)
# Floor to current-stack start — older log entries belong to a different backend
if [[ "$SINCE" < "$STACK_START" ]]; then
    echo "(NOTE: requested window starts before current Q8 stack date $STACK_START — flooring SINCE to $STACK_START)"
    SINCE="$STACK_START"
fi

echo "=== compression events since $SINCE ==="
grep -E "Auxiliary compression: using" "$LOG" \
  | awk -v since="$SINCE" '$1 >= since' \
  | awk '{print $1, $2, $NF, $(NF-1)}' \
  | tail -30

echo
echo "=== failures since $SINCE ==="
grep -E "Context compression failed" "$LOG" \
  | awk -v since="$SINCE" '$1 >= since' \
  | tail -10

echo
echo "=== top 10 biggest API calls (in= tokens) since $SINCE ==="
grep -E "API call #" "$LOG" \
  | awk -v since="$SINCE" '$1 >= since' \
  | grep -oE "in=[0-9]+" \
  | sort -t= -k2 -rn \
  | head -10

echo
echo "=== daily compression count ==="
grep -E "Auxiliary compression: using" "$LOG" \
  | awk -v since="$SINCE" '$1 >= since {print $1}' \
  | sort | uniq -c

echo
echo "=== currently routed to (from last-used coder config) ==="
grep -E "summary_base_url|compression:" -A 5 ~/.hermes/profiles/coder/config.yaml \
  | grep -E "model|base_url" \
  | head -6
