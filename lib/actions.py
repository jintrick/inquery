import json
import sys
from typing import List, Dict, Any, Optional

class Action:
    """
    アクション1件のデータモデル。
    """
    def __init__(self, data: Dict[str, Any]):
        self.label: str = data.get("label", "")
        self.url: Optional[str] = data.get("url")
        self.script: Optional[str] = data.get("script")
        self.args: List[str] = data.get("args", [])
        self.show_if_contains: Optional[List[str]] = data.get("show_if_contains")
        self.copy_to_clipboard: bool = data.get("copy_to_clipboard", False)
        self.raw_data = data

    @property
    def type(self) -> str:
        """
        URLかScriptかを自動判別する。両方ある場合はURLを優先。
        """
        if self.url:
            return "url"
        if self.script:
            return "script"
        return "unknown"

    def is_clipboard_only(self) -> bool:
        return self.copy_to_clipboard

    def matches_constraint(self, query: str) -> bool:
        """
        クエリが制約条件(show_if_contains)を満たすか判定する。
        制約がない場合は常にTrueを返す。
        """
        if not self.show_if_contains:
            return True
        return any(char in query for char in self.show_if_contains)


class ActionRepository:
    """
    設定ファイル(JSON)からActionコレクションを読み込み・管理するリポジトリ。
    """
    def __init__(self, config_path: str):
        self.config_path = config_path

    def list_all(self) -> List[Action]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
        except Exception as e:
            print(f"Error loading actions: {e}", file=sys.stderr)
            sys.exit(1)

        actions_data: List[Dict[str, Any]] = data.get("actions", [])
        return [Action(a) for a in actions_data]


class ActionFilter:
    """
    クエリに基づき、アクションを抽出する純粋なドメインロジック。
    """
    @staticmethod
    def filter(actions: List[Action], query: str) -> List[Action]:
        # 1. 改行が含まれる場合：クリップボードコピー対応のアクションのみを強制抽出
        if "\n" in query:
            return [a for a in actions if a.is_clipboard_only()]

        # 2. 改行がない場合：show_if_contains 制約を満たすもののみを抽出
        # （ラベル名による部分一致検索は行わない）
        return [a for a in actions if a.matches_constraint(query)]


class ActionOrchestrator:
    """
    データのロードからフィルタリング、出力までのパイプラインを指揮する。
    """
    @staticmethod
    def run(query: str, config_path: str) -> None:
        repo = ActionRepository(config_path)
        all_actions = repo.list_all()
        
        filtered_actions = ActionFilter.filter(all_actions, query)
        
        for action in filtered_actions:
            print(action.label)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: actions.py <query> <config_path>", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    config_path = sys.argv[2]
    
    ActionOrchestrator.run(query, config_path)
