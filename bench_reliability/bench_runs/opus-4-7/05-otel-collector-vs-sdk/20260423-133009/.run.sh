#!/bin/bash
cd /tmp/bench_ceiling/05-otel-collector-vs-sdk_20260423-133009-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/05-otel-collector-vs-sdk_20260423-133009-f/.prompt.txt)" > /tmp/bench_ceiling/05-otel-collector-vs-sdk_20260423-133009-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/05-otel-collector-vs-sdk_20260423-133009-f/.done
