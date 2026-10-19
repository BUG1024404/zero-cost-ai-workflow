#!/bin/bash
# 每日免费模型扫描。用法：把下面这行加入 crontab（crontab -e）：
#   0 8 * * * /path/to/zero-cost-ai-workflow/freetoken-scan/scan.sh
#
# 依赖：
#   1. https://github.com/limin112/min-skill 已 clone 到 ~/min-skill
#   2. OpenRouter key 存在 ~/.pi/agent/.openrouter_key（600 权限），内容为 key 本体、无换行
set -euo pipefail

SKILL_DIR="$HOME/min-skill/skills/FreeToken-Bots"
KEY_FILE="$HOME/.pi/agent/.openrouter_key"
LOG_FILE="$HOME/.pi/agent/freetoken-scan.log"

if [ ! -f "$KEY_FILE" ]; then
  echo "$(date -Is) ERROR: key file not found: $KEY_FILE" >> "$LOG_FILE"
  exit 1
fi

export OPENROUTER_API_KEY
OPENROUTER_API_KEY="$(tr -d '\n' < "$KEY_FILE")"

cd "$SKILL_DIR"
python3 scripts/radar.py scan >> "$LOG_FILE" 2>&1
echo "$(date -Is) scan done" >> "$LOG_FILE"
