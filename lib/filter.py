import json
import sys
from typing import List, Dict, Any, Optional

def filter_actions(query: str, config_path: str) -> List[str]:
    """
    Filters action labels based on the user query.
    If no matches are found or query is empty, returns all labels.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
    except Exception as e:
        print(f"Error loading actions: {e}", file=sys.stderr)
        sys.exit(1)

    actions: List[Dict[str, Any]] = data.get("actions", [])
    query_lower = query.lower()

    # Filtering logic: matches query within label
    filtered: List[str] = [
        a["label"] for a in actions 
        if not query or query_lower in a.get("label", "").lower()
    ]

    # Fallback: if filtering results in nothing but a query was provided, return all
    if not filtered:
        filtered = [a["label"] for a in actions]

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
