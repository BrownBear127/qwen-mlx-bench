#!/bin/bash
cd /tmp/bench_ceiling/03-sqlite-migration_20260423-132803-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/03-sqlite-migration_20260423-132803-f/.prompt.txt)" > /tmp/bench_ceiling/03-sqlite-migration_20260423-132803-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/03-sqlite-migration_20260423-132803-f/.done
