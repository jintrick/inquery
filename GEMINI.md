# inquery — AIエージェント向け指示書

## プロジェクト概要

**inquery** は Ubuntu (X11) 向けの Zenity ベースのキーボードドリブン検索ランチャーです。

設計の核心は**名詞先行・動詞後選択**です。ユーザーはまず「調べたいもの」を入力し、その後「どこで検索するか」をリストから選びます。

---

## 設計上の絶対原則（Deterministic Design）

1. **Dynamic Filtering**: ユーザー入力（クエリ）に基づき、アクションリストの絞り込み（フィルタリング）を許可する。ただし、デフォルトでは全アクションを表示の候補とすること。
2. **Prefix-Free**: アクション起動のためのプレフィックス入力を禁止する。
3. **Subject-Predicate Order**: 名詞（検索ワード）入力 → 動詞（アクション）選択の順序を厳守せよ。
4. **Zenity Interaction**: UIは `zenity` の標準機能（`--entry` および `--list`）を組み合わせて実現せよ。

---

## 動作環境

- **OS**: Ubuntu 22.04 LTS 以降
- **ディスプレイサーバー**: X11
- **コア依存**: `zenity`, `bash`, `python3` (Python 3.10以上)
- **ブラウザ起動**: `xdg-open`

---

## 成果物構成（File-Based Architecture）

```
inquery/
├── bin/
│   └── inquery         # メインエントリーポイント（Executable Bash/Python script）
├── lib/
│   ├── ui.sh           # Zenity 呼び出しラッパー
│   └── executor.py     # 実行ロジック（URL置換、subprocess実行）
├── config/
│   └── actions.json.example
├── README.md
├── GEMINI.md
└── pyproject.toml
```

---

## 各モジュールの責務（Atomic Responsibilities）

### `bin/inquery`
- エントリーポイント。
- ユーザーからの入力を受け取り（`zenity --entry`）、その結果を `ui.sh` に渡す。

### `lib/ui.sh`
- `zenity --list` を使用したアクション選択インターフェースの提供。
- アクションリストを `config/actions.json` から読み込み、表示する。
- 選択されたアクションとクエリを `executor.py` に渡す。

### `lib/executor.py`
- アクションの実行。
- `type: "url"`: URL内の `{query}` を `urllib.parse.quote_plus` で置換し `xdg-open` で開く。
- `type: "script"`: 引数内の `{query}` を置換し `subprocess.Popen` で非同期実行する。

---

## actions.json スキーマ

```json
{
  "actions": [
    {
      "label": "Googleで検索",
      "type": "url",
      "url": "https://www.google.com/search?q={query}"
    },
    {
      "label": "カスタムスクリプト",
      "type": "script",
      "script": "/path/to/script.sh",
      "args": ["{query}"]
    }
  ]
}
```

---

## 開発・コーディング規約（High-Signal Standards）

- **UI Implementation**: GTK4/PyGObject を廃止し、`zenity` による実装に一本化せよ。
- **No Global State**: 依存関係は明示的に引数で渡せ。
- **Error Handling**: エラー発生時は `zenity --error` でユーザーに通知するか、stderr に出力せよ。
- **Python Code**: 型ヒント必須。`ruff` でフォーマットせよ。
- **Atomic Commits**: 機能変更は原子的な単位で行え。

---

## 禁止事項と代替行動（Constraints & Fallbacks）

| 禁止事項 | 代替行動 |
|----------|----------|
| GTK4 / PyGObject の使用 | `zenity` を使用して UI を構築せよ |
| プレフィックスによるアクション選択 | クエリ入力後のリスト選択、または入力に応じた自動フィルタリングで対応せよ |
| `sudo` の使用 | ユーザー権限で動作する実装を行え |
| ブロッキング処理 | 実行（URL/Script）は非同期で行い、UIを即座に解放せよ |

---

## 完了判定チェックリスト

- [x] `zenity` ベースのプロトタイプが動作する
- [x] 名詞（クエリ）入力後に動詞（アクション）選択画面が表示される
- [x] 入力内容に応じたアクションのフィルタリング機能が動作する
- [x] URL置換およびスクリプト実行が正しく機能する
