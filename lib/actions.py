import json
import sys
from abc import ABC, abstractmethod
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
        URLかScriptかを自動判別する。
        """
        if self.url:
            return "url"
        if self.script:
            return "script"
        return "unknown"

    def matches_constraint(self, query: str) -> bool:
        """
        クエリが制約条件(show_if_contains)を満たすか判定する。
        """
        if not self.show_if_contains:
            return False
        return any(char in query for char in self.show_if_contains)


class FilterLayer(ABC):
    """
    フィルタリングの1階層(レイヤー)を表す抽象基底クラス。
    """
    def __init__(self, priority: int):
        self.priority = priority

    @abstractmethod
    def is_applicable(self, query: str, actions: List[Action]) -> bool:
        """このレイヤーを適用すべき状況か判定する。"""
        pass

    @abstractmethod
    def apply(self, query: str, actions: List[Action]) -> List[Action]:
        """アクションをフィルタリングする。"""
        pass


class NewlineLayer(FilterLayer):
    """
    改行が含まれる場合、クリップボード用アクションのみを独占表示するレイヤー。
    """
    def __init__(self):
        super().__init__(priority=100)

    def is_applicable(self, query: str, actions: List[Action]) -> bool:
        return "\n" in query

    def apply(self, query: str, actions: List[Action]) -> List[Action]:
        return [a for a in actions if a.copy_to_clipboard]


class ConstraintLayer(FilterLayer):
    """
    クエリが制約文字に合致した場合、そのアクションのみを独占表示するレイヤー。
    """
    def __init__(self):
        super().__init__(priority=50)

    def is_applicable(self, query: str, actions: List[Action]) -> bool:
        return any(a.matches_constraint(query) for a in actions if a.show_if_contains)

    def apply(self, query: str, actions: List[Action]) -> List[Action]:
        return [a for a in actions if a.show_if_contains and a.matches_constraint(query)]


class DefaultLayer(FilterLayer):
    """
    制約を持たないアクションを標準表示するレイヤー。
    """
    def __init__(self):
        super().__init__(priority=0)

    def is_applicable(self, query: str, actions: List[Action]) -> bool:
        return True

    def apply(self, query: str, actions: List[Action]) -> List[Action]:
        # 制約を持たないもの、または適合する上位レイヤーがない場合のフォールバック
        return [a for a in actions if not a.show_if_contains]


class ActionRepository:
    """
    設定ファイルからActionコレクションを読み込む。
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._cached_actions: Optional[List[Action]] = None

    def list_all(self) -> List[Action]:
        if self._cached_actions is not None:
            return self._cached_actions

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
        except Exception as e:
            print(f"Error loading actions: {e}", file=sys.stderr)
            sys.exit(1)

        actions_data: List[Dict[str, Any]] = data.get("actions", [])
        self._cached_actions = [Action(a) for a in actions_data]
        return self._cached_actions


class ActionFilter:
    """
    優先度付きレイヤーを用いてアクションをフィルタリングする。
    """
    def __init__(self):
        # 優先度順にレイヤーを保持
        self.layers: List[FilterLayer] = sorted(
            [NewlineLayer(), ConstraintLayer(), DefaultLayer()],
            key=lambda l: l.priority,
            reverse=True
        )

    def filter(self, query: str, actions: List[Action]) -> List[Action]:
        for layer in self.layers:
            if layer.is_applicable(query, actions):
                return layer.apply(query, actions)
        return []


class ActionOrchestrator:
    """
    全体のパイプラインを指揮する。
    """
    @staticmethod
    def run(query: str, config_path: str) -> None:
        repo = ActionRepository(config_path)
        actions = repo.list_all()
        
        filter_engine = ActionFilter()
        filtered_actions = filter_engine.filter(query, actions)
        
        for action in filtered_actions:
            print(action.label)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: actions.py <query> <config_path>", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    config_path = sys.argv[2]
    
    ActionOrchestrator.run(query, config_path)
