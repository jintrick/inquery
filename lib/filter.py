import json
import sys
from typing import List, Dict, Any, Optional

def filter_actions(query: str, config_path: str) -> List[str]:
    """
    Filters action labels based on the user query.
    If no matches are found or query is empty, returns all labels (excluding those with 
    unmatched show_if_contains constraints).
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
    except Exception as e:
        print(f"Error loading actions: {e}", file=sys.stderr)
        sys.exit(1)

    actions: List[Dict[str, Any]] = data.get("actions", [])
    
    # 改行が含まれる場合、copy_to_clipboard: true のアクションのみに絞り込み、そのまま返す
    if "\n" in query:
        return [a["label"] for a in actions if a.get("copy_to_clipboard") is True]

    if not query:
        return [a["label"] for a in actions]

    query_lower = query.lower()
    filtered: List[str] = []

    for a in actions:
        label = a.get("label", "")
        show_if_contains = a.get("show_if_contains")
        
        if query_lower in label.lower():
            filtered.append(label)
        elif show_if_contains is not None:
            if any(char in query for char in show_if_contains):
                filtered.append(label)

    # Fallback: if filtering results in nothing but a query was provided, 
    # return all actions that do not have explicit show_if_contains constraints.
    if not filtered:
        filtered = [a["label"] for a in actions if a.get("show_if_contains") is None]

    return filtered

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: filter.py <query> <config_path>", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    config_path = sys.argv[2]
    
    labels = filter_actions(query, config_path)
    for label in labels:
        print(label)

if __name__ == "__main__":
    main()
