#!/bin/bash
# ui.sh - Zenity list wrapper

QUERY="$1"
APP_ROOT="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
FILTER_SCRIPT="$APP_ROOT/lib/filter.py"
EXECUTOR_SCRIPT="$APP_ROOT/lib/executor.py"

# Configuration fallback logic
USER_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/inquery/actions.json"
DEFAULT_CONFIG="$APP_ROOT/config/actions.json"
EXAMPLE_CONFIG="$APP_ROOT/config/actions.json.example"

if [ -f "$USER_CONFIG" ]; then
    CONFIG_FILE="$USER_CONFIG"
elif [ -f "$DEFAULT_CONFIG" ]; then
    CONFIG_FILE="$DEFAULT_CONFIG"
elif [ -f "$EXAMPLE_CONFIG" ]; then
    CONFIG_FILE="$EXAMPLE_CONFIG"
else
    zenity --error --text="設定ファイルが見つかりません。インストール状況を確認してください。"
    exit 1
fi

# Extract labels using separate filter script
LABELS=$(python3 "$FILTER_SCRIPT" "$QUERY" "$CONFIG_FILE")

if [ $? -ne 0 ]; then
    # Error message is likely already printed to stderr by python script
    exit 1
fi

# Show selection list
SELECTED_LABEL=$(echo "$LABELS" | zenity --list --title="inquery - $QUERY" --column="アクション" --width=400 --height=300 --text="実行するアクションを選択してください:")

# If an action was selected, execute it
if [ $? -eq 0 ] && [ -n "$SELECTED_LABEL" ]; then
    python3 "$EXECUTOR_SCRIPT" "$SELECTED_LABEL" "$QUERY" "$CONFIG_FILE"
fi
