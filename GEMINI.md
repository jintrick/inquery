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
5. **Configuration Fallback**: ユーザー設定（`~/.config`）を優先しつつ、システムデフォルトでも即座に動作する堅牢な探索ロジックを維持せよ。

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
│   └── inquery         # メインエントリーポイント（readlink -f によるパス解決）
├── lib/
│   ├── ui.sh           # Zenity 呼び出しラッパー（XDG設定フォールバック実装）
│   ├── filter.py       # アクションのフィルタリングロジック（型ヒント付き）
│   └── executor.py     # 実行ロジック（URL置換、subprocess実行、Zenityエラー通知）
├── config/
│   ├── actions.json    # デフォルト設定
│   └── actions.json.example
├── assets/
│   └── inquery.desktop.example # デスクトップ統合用テンプレート
├── scripts/
│   └── run_tests.sh    # テストランナー（静的解析・ユニットテスト・統合テスト）
├── tests/              # 各種テストコード
├── install.sh          # 自動インストーラー
├── README.md
├── GEMINI.md
└── pyproject.toml
```

---

## 各モジュールの責務（Atomic Responsibilities）

### `bin/inquery`
- エントリーポイント。
- 実行ファイルの絶対パスを特定し、ユーザーからの入力を受け取って `ui.sh` に渡す。
- **入力モードの管理**: 1行入力プロンプトを表示。`..` が入力された場合は複数行入力モード（Zenity `--text-info`）へ遷移する。

### `lib/ui.sh`
- `zenity --list` を使用したアクション選択インターフェースの提供。
- XDG 規約に基づき `actions.json` を優先順位付きで探索する。
- `actions.py` (旧 filter.py) を呼び出してラベルを抽出し、選択された結果を `executor.py` に渡す。
- 実行失敗時はエラー内容をキャプチャし、Zenity で表示する。

### `lib/actions.py`
- アクションリストからのラベル抽出と、クエリに基づいたフィルタリング。
- **フィルタリングルール**:
    - クエリに改行が含まれる場合：`copy_to_clipboard: true` のアクションのみを表示。
    - 改行がない場合：`show_if_contains` 制約を満たすアクションを表示（制約がないものは常に表示）。
    - *注意*: ラベル名による部分一致検索は行わない。

### `lib/executor.py`
- アクションの実行。URL置換またはスクリプト実行。
- 失敗時は `zenity --error` を用いてユーザーに通知する。

---

## 開発・コーディング規約（High-Signal Standards）

- **UI Implementation**: `zenity` による実装に一本化せよ。
- **Type Safety**: Python コードには型ヒントを必須とし、`ruff` でフォーマットせよ。
- **Distribution Readiness**: 
    - 全実行スクリプトに実行権限（`+x`）を付与せよ。
    - `install.sh` による「一発インストール」体験を維持せよ。
- **Quality Assurance**: 
    - 変更時は必ず `scripts/run_tests.sh` をパスさせること。
    - インストーラーやパス解決の挙動は `tests/` 内の統合テストで担保せよ。
- **Git Workflow**:
    - デフォルトブランチは `master` を使用せよ。`main` は使用しない。

---

## 禁止事項と代替行動（Constraints & Fallbacks）

| 禁止事項 | 代替行動 |
|----------|----------|
| GTK4 / PyGObject の使用 | `zenity` を使用して UI を構築せよ |
| 固定の相対パス依存 | `readlink -f` 等を用いた絶対パス解決を行え |
| ユーザー環境の強制書き換え | 設定ファイルはフォールバック方式で読み込み、インストールは配置に専念せよ |

---

## 完了判定チェックリスト

- [x] `zenity` ベースのプロトタイプが動作する
- [x] 名詞（クエリ）入力後に動詞（アクション）選択画面が表示される
- [x] 入力内容に応じたアクションのフィルタリング機能が動作する
- [x] URL置換およびスクリプト実行が正しく機能する
- [x] テストフレームワークにより品質が自動検証されている
- [x] 自動インストーラーにより導入の障壁が解消されている
