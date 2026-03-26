#!/bin/bash
LOG_FILE="logs/format-py.log"
file_path=$(jq -r '.tool_input.file_path // empty')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] file_path=$file_path" >> "$LOG_FILE"

if [[ "$file_path" == *.py ]]; then
    output=$(uv run ruff format "$file_path" 2>&1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $output" >> "$LOG_FILE"
fi
