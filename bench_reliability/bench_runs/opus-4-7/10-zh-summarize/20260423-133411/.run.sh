#!/bin/bash
cd /tmp/bench_ceiling/10-zh-summarize_20260423-133411-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/10-zh-summarize_20260423-133411-f/.prompt.txt)" > /tmp/bench_ceiling/10-zh-summarize_20260423-133411-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/10-zh-summarize_20260423-133411-f/.done
