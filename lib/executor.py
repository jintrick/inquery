import json
import sys
import subprocess
import urllib.parse
import os
from typing import List, Dict, Any, Optional

def notify_error(message: str) -> None:
    """Displays an error message using zenity."""
    subprocess.run(["zenity", "--error", "--text", message], check=False)

def execute() -> None:
    if len(sys.argv) < 4:
        print("Usage: executor.py <label> <query> <config_path>", file=sys.stderr)
        sys.exit(1)

    label: str = sys.argv[1]
    query: str = sys.argv[2]
    config_path: str = sys.argv[3]

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
    except Exception as err:
        err_msg = f"設定ファイルの読み込みに失敗しました:\n{err}"
        print(err_msg, file=sys.stderr)
        notify_error(err_msg)
        sys.exit(1)

    actions: List[Dict[str, Any]] = data.get("actions", [])
    action: Optional[Dict[str, Any]] = next(
        (a for a in actions if a["label"] == label), None
    )

    if not action:
        err_msg = f"アクションが見つかりません: {label}"
        print(err_msg, file=sys.stderr)
        notify_error(err_msg)
        sys.exit(1)

    try:
        if action["type"] == "url":
            url: str = action["url"].replace("{query}", urllib.parse.quote_plus(query))
            subprocess.Popen(["xdg-open", url], start_new_session=True)
        elif action["type"] == "script":
            script_path: str = os.path.expanduser(action["script"])
            args: List[str] = [
                arg.replace("{query}", query) for arg in action.get("args", [])
            ]
            subprocess.Popen([script_path] + args, start_new_session=True)
    except Exception as err:
        err_msg = f"実行中にエラーが発生しました:\n{err}"
        print(err_msg, file=sys.stderr)
        notify_error(err_msg)
        sys.exit(1)

if __name__ == "__main__":
    execute()
