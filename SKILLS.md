# SKILLS.md

このプロジェクトで繰り返し発生する定型作業の手順集。エージェントが「どう作業を進めるか」を素早く判断するためのレシピ。前提はルートの [`AGENTS.md`](AGENTS.md) を参照。

## スキル一覧

- [新しい記事を書く](#新しい記事を書く)
- [記事を編集してレンダーする](#記事を編集してレンダーする)
- [ローカルプレビューを起動する](#ローカルプレビューを起動する)
- [テーマ・スタイルを変更する](#テーマスタイルを変更する)
- [環境を新しいマシンにセットアップする](#環境を新しいマシンにセットアップする)
- [autosync の競合から復旧する](#autosync-の競合から復旧する)

---

### 新しい記事を書く

1. カテゴリのサブディレクトリを決める（新テーマなら新規作成）。→ [`posts/AGENTS.md`](posts/AGENTS.md)
2. テンプレートを複製: `cp posts/play_ground/template.qmd posts/<category>/<slug>.qmd`
3. Frontmatter（`title` / `date` / `categories` / `image`）を埋め、TODO コメントを削除。
4. 本文を日本語で執筆（見出しは `##` から）。
5. 単一ファイルレンダー: `uv run quarto render posts/<category>/<slug>.qmd`
6. 更新された `.qmd` と `_site/` をまとめてコミット。

### 記事を編集してレンダーする

1. 対象 `.qmd` を編集。
2. `uv run quarto render posts/<category>/<file>.qmd`（サイト全体を再レンダーする必要はない）。
3. 生成された `_site/` の差分も一緒にコミットする。

### ローカルプレビューを起動する

```bash
uv run quarto preview
```

- ホットリロードで変更が即反映。プレビューのホットキーは `⌘ + ⇧ + K`。
- VS Code の Quarto 拡張は `scripts/quarto` ラッパー経由で同じ環境を使う。

### テーマ・スタイルを変更する

- 配色・テーマ: `_scss/theme-glass-dark.scss` / `_scss/theme-glass-light.scss`
- 汎用スタイル: `styles.css`
- HTML ヘッダへの差し込み: `_includes/`（plotly 設定・サイドバートグル）
- 変更後は `uv run quarto render` で全体を再ビルドして反映を確認。

### 環境を新しいマシンにセットアップする

```bash
uv python install
direnv allow
uv sync
python -m ipykernel install --user --name quarto-notes --display-name "Python (quarto-notes)"
```

autosync も使うなら: `./scripts/install-autosync.sh`（launchd に 5 分間隔で登録。冪等）。

### autosync の競合から復旧する

macOS 通知で「autosave/\<hostname\> に退避しました」等が来た場合の手順は
[`scripts/AUTOSYNC.md`](scripts/AUTOSYNC.md) の「競合時の復旧手順」を参照。要点:

1. `git fetch origin && git log origin/main..origin/autosave/<hostname>` で差分確認。
2. ローカル `main` で `git rebase origin/main` して競合解消。
3. `git push origin main`。
4. `git push origin --delete autosave/<hostname>` で退避ブランチ削除。
5. `./scripts/autosync.sh` を一度手動実行し `.git/autosync-notified` フラグが消えることを確認。
