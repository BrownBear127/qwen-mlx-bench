#!/bin/bash
cd /tmp/bench_ceiling/06-rss-dedupe_20260423-133042-f
~/.local/bin/claude --print --model opus --add-dir . --permission-mode bypassPermissions -p "$(cat /tmp/bench_ceiling/06-rss-dedupe_20260423-133042-f/.prompt.txt)" > /tmp/bench_ceiling/06-rss-dedupe_20260423-133042-f/.claude_output.txt 2>&1
echo $? > /tmp/bench_ceiling/06-rss-dedupe_20260423-133042-f/.done
