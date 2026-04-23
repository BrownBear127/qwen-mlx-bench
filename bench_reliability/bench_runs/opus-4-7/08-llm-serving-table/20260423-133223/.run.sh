#!/bin/bash
cd /tmp/bench_ceiling/08-llm-serving-table_20260423-133223-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/08-llm-serving-table_20260423-133223-f/.prompt.txt)" > /tmp/bench_ceiling/08-llm-serving-table_20260423-133223-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/08-llm-serving-table_20260423-133223-f/.done
