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
