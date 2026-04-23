#!/bin/bash
cd /tmp/bench_ceiling/09-svg-diff_20260423-133300-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/09-svg-diff_20260423-133300-f/.prompt.txt)" > /tmp/bench_ceiling/09-svg-diff_20260423-133300-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/09-svg-diff_20260423-133300-f/.done
