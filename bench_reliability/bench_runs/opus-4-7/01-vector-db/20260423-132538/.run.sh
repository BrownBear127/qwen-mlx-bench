#!/bin/bash
cd /tmp/bench_ceiling/01-vector-db_20260423-132538-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/01-vector-db_20260423-132538-f/.prompt.txt)" > /tmp/bench_ceiling/01-vector-db_20260423-132538-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/01-vector-db_20260423-132538-f/.done
