#!/bin/bash
cd /tmp/bench_ceiling/07-fragile-install-fallback_20260423-133135-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/07-fragile-install-fallback_20260423-133135-f/.prompt.txt)" > /tmp/bench_ceiling/07-fragile-install-fallback_20260423-133135-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/07-fragile-install-fallback_20260423-133135-f/.done
