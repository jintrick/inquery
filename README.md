# inquery

**inquery** は Ubuntu (X11) 向けの Zenity ベースのキーボードドリブン検索ランチャーです。
「名詞先行・動詞後選択」の設計思想に基づき、素早い検索体験を提供します。

## Quick Start (推奨)

リポジトリをクローンして、インストールスクリプトを実行するだけで準備完了です。

```bash
git clone https://github.com/youruser/inquery.git
cd inquery
./install.sh
```

インストール後、アプリケーションメニュー（Ubuntu Dash等）から `inquery` を起動するか、ターミナルで `inquery` と入力してください。

## 使い方

1. `inquery` を起動すると、1行入力プロンプトが表示されます。
2. 検索ワード（名詞）を入力して Enter を押すと、実行可能なアクション（動詞）の一覧が表示されます。
3. アクションを選択すると、ブラウザが開くか、スクリプトが実行されます。

### 複数行入力モード
入力プロンプトで `..`（ピリオド2つ）を入力して Enter を押すと、複数行入力用のエディタが開きます。
- 長文の翻訳や、コードの整形などに便利です。
- 複数行入力時は、設定ファイルで `copy_to_clipboard: true` が設定されているアクションのみが選択肢として表示されます。

### 設定例 (`actions.json`)

1つのスクリプトに対し、引数（`args`）を切り替えることで異なる動作（例：大文字変換・小文字変換）をさせる設定例です。

```json
{
  "actions": [
    {
      "label": "Googleで検索",
      "url": "https://www.google.com/search?q={query}"
    },
    {
      "label": "大文字に変換",
      "script": "~/.config/inquery/scripts/convert.sh",
      "args": ["--upper", "{query}"]
    },
    {
      "label": "小文字に変換",
      "script": "~/.config/inquery/scripts/convert.sh",
      "args": ["--lower", "{query}"]
    }
  ]
}
```

- **`url`**: ブラウザで開くURL。`{query}` はURLエンコードされて埋め込まれます。
- **`script`**: 実行ファイルのパス。`~`（ホームディレクトリ）を使用可能です。
- **`args`**: スクリプトに渡す引数のリスト。
    - `{query}` はユーザーが入力した文字列に置換されます。
    - **スクリプト側の受け取り**: 上記の「大文字に変換」の場合、スクリプト内では `$1` に `--upper`、`$2` に入力した文字列が格納されます。
    - **安全性**: 引数をリスト形式（`["--upper", "{query}"]`）で記述することで、入力内容にスペースが含まれていても、シェルインジェクションを防ぎ安全に処理されます。

---

## 依存関係
- `zenity`, `bash`, `python3` (3.10以上)

## ライセンス
MIT

## Appendix: Advanced Installation (手動設定)
自動スクリプトを使わずに設定したい場合は、以下の手順を実行してください。

1. `bin/inquery` へのシンボリックリンクをパスの通ったディレクトリ（`~/.local/bin` 等）に作成します。
2. `assets/inquery.desktop.example` を `~/.local/share/applications/inquery.desktop` にコピーし、`Exec` パスを絶対パスに書き換えます。
