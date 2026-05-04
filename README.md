# inquery

**inquery** は Ubuntu (X11) 向けの Zenity ベースのキーボードドリブン検索ランチャーです。
「名詞先行・動詞後選択（Subject-Predicate Order）」の設計思想に基づき、素早い検索体験を提供します。

## インストール方法

### 1. リポジトリのクローン
```bash
git clone https://github.com/youruser/inquery.git
cd inquery
```

### 2. シンボリックリンクの作成
実行ファイルへのシンボリックリンクを `~/.local/bin` などに作成します。
```bash
ln -s $(pwd)/bin/inquery ~/.local/bin/inquery
```

### 3. デスクトップ統合（任意）
アプリケーションランチャーから起動できるようにするには、以下の操作を行います。
```bash
mkdir -p ~/.local/share/applications
cp assets/inquery.desktop.example ~/.local/share/applications/inquery.desktop
# Exec のパスを実際の場所に合わせて書き換えてください
sed -i "s|/path/to/inquery|$(pwd)|g" ~/.local/share/applications/inquery.desktop
```

## カスタマイズ

設定ファイル（`actions.json`）を編集することで、独自の検索アクションを追加できます。

1. 設定ディレクトリを作成します。
   ```bash
   mkdir -p ~/.config/inquery
   ```
2. デフォルトの設定をコピーします。
   ```bash
   cp config/actions.json.example ~/.config/inquery/actions.json
   ```
3. `~/.config/inquery/actions.json` を自由に編集してください。

### 設定例
```json
{
  "actions": [
    {
      "label": "Googleで検索",
      "type": "url",
      "url": "https://www.google.com/search?q={query}"
    },
    {
      "label": "GitHubで検索",
      "type": "url",
      "url": "https://github.com/search?q={query}"
    }
  ]
}
```

## 依存関係
- `zenity`
- `bash`
- `python3` (3.10以上)

## ライセンス
MIT
