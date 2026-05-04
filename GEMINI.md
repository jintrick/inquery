# inquery — AIエージェント向け指示書

## プロジェクト概要

**inquery** は Ubuntu (X11) 向けの GTK4 製キーボードドリブン検索ランチャーです。

設計の核心は**名詞先行・動詞後選択**です。ユーザーはまず「調べたいもの」を入力し、その後「どこで検索するか」をリストから選びます。プレフィックス型ランチャー（例：「g 検索ワード」）とは対極の設計です。アクションリストは入力内容に関わらず常に全件表示します。

---

## 設計上の絶対原則（違反禁止）

1. **フィルタリング禁止**: ユーザーの入力に基づいてアクションリストを絞り込んではならない。ファジーマッチも同様。
2. **プレフィックス禁止**: アクションを起動するためにプレフィックス（例：「g 」「yt 」）の入力をユーザーに求めてはならない。
3. **並列表示**: 全アクションは起動直後から同時に表示される。
4. **名詞→動詞の順序**: ユーザーが主語（検索ワード）を入力してから、述語（アクション）を選ぶ。

---

## 動作環境

- **OS**: Ubuntu 22.04 LTS 以降（apt系ディストリビューション）
- **ディスプレイサーバー**: X11
- **UIツールキット**: GTK4 / PyGObject（`python3-gi`、`gir1.2-gtk-4.0`）
- **Python**: 3.10以上

---

## ディレクトリ構成

```
inquery/
├── inquery/
│   ├── __init__.py
│   ├── main.py          # エントリポイント、Gtk.Applicationサブクラス
│   ├── window.py        # LauncherWindow（GTK4 UI・CSS・イベントハンドラ）
│   ├── actions.py       # JSON読み込み、Actionデータクラス定義
│   └── executor.py      # 実行ロジック（url → xdg-open、script → subprocess）
├── config/
│   └── actions.json.example
├── scripts/
│   └── example_script.sh
├── tests/
│   └── test_actions.py
├── .gitignore
├── README.md
├── gemini.md
└── pyproject.toml
```

---

## 各モジュールの責務

### `inquery/actions.py`
- `Action` データクラスの定義
- `load_actions(path: Path) -> list[Action]` — `actions.json` の読み込みとバリデーション
- 設定ファイルの場所: `~/.config/inquery/actions.json`
- 初回起動時にファイルが存在しなければデフォルト設定を自動生成する

### `inquery/executor.py`
- `execute(action: Action, query: str) -> None`
- `type: "url"` → URLの `{query}` を置換して `xdg-open` に渡す
- `type: "script"` → argsの `{query}` を置換して `subprocess.Popen` で呼び出す
- 非同期実行（ノンブロッキング）

### `inquery/window.py`
- `LauncherWindow(Gtk.ApplicationWindow)`
- キー入力のたびにアクションリストを全件再描画（フィルタリングなし）
- 各行の表示: クエリが空でない場合は `{アクション名}  「{query}」` の形式
- キーボード操作: `↑↓` で移動、`Enter` で実行、`Escape` で終了
- 行クリックでも実行

### `inquery/main.py`
- `LauncherApp(Gtk.Application)`
- 起動時にアクションをロード
- `LauncherWindow` を生成
- `main()` が `pyproject.toml` から呼ばれるエントリポイント

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
      "label": "スクリプト例",
      "type": "script",
      "script": "~/.config/inquery/scripts/example.sh",
      "args": ["{query}"]
    }
  ]
}
```

- `{query}` は実行時に置換されるプレースホルダー
- URLクエリは `urllib.parse.quote_plus` でパーセントエンコードする
- `type` は `"url"` または `"script"` のいずれか

---

## コーディング規約

- **型ヒント**: 全関数・メソッドに必須
- **フォーマッター**: ruff
- **docstring**: Google スタイル
- **Pythonバージョン**: 3.10以上。適宜 `match` 文を使うこと
- **グローバル状態禁止**: 依存は明示的に渡すこと
- **データクラス**: データ構造には `dict` ではなく `@dataclass` を使うこと
- **エラーハンドリング**: 例外を黙って握りつぶさないこと。エラーは stderr に出力する

---

## pyproject.toml のエントリポイント

```toml
[project.scripts]
inquery = "inquery.main:main"
```

---

## やってはいけないこと

- `sudo` の使用や root 権限の前提
- `os.system()` の使用 → `subprocess.Popen` を使うこと
- GTKメインループのブロック → 非同期処理は `GLib.idle_add` またはスレッドを使うこと
- パスのハードコード → `Path.home() / ".config" / "inquery"` を使うこと
- ユーザー入力によるアクションリストのフィルタリング・ソート
- プレフィックス起動構文の追加
- KDE・GNOME Shell などの重いデスクトップ環境への依存の導入
