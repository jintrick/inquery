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

## カスタマイズ

自分専用の検索アクションを追加するには、設定ファイルを作成します。

```bash
mkdir -p ~/.config/inquery
cp config/actions.json.example ~/.config/inquery/actions.json
```
その後、`~/.config/inquery/actions.json` を自由に編集してください。

---

## 依存関係
- `zenity`, `bash`, `python3` (3.10以上)

## ライセンス
MIT

## Appendix: Advanced Installation (手動設定)
自動スクリプトを使わずに設定したい場合は、以下の手順を実行してください。

1. `bin/inquery` へのシンボリックリンクをパスの通ったディレクトリ（`~/.local/bin` 等）に作成します。
2. `assets/inquery.desktop.example` を `~/.local/share/applications/inquery.desktop` にコピーし、`Exec` パスを絶対パスに書き換えます。
