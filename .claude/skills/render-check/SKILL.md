---
name: render-check
description: 記事や設定を変更した後のレンダー確認と公開準備。quarto render の実行、プレビュー確認、_site/ のコミットまで。変更を検証・公開したいときに使う。
---

# レンダー確認と公開準備

## 1. レンダーする

`uv run quarto`(または `scripts/quarto` ラッパー)経由で実行する。素の `quarto` は `.venv` 外の Python を掴むことがある。

```bash
uv run quarto render "posts/<category>/<file>.qmd"   # 記事単体(速い。index/sidebar も追従更新)
uv run quarto render                                 # サイト全体(_quarto.yml や theme を触った場合)
```

- `freeze: auto` のため、実行セルを変更していない記事は再実行されない。
- Python セル・Plotly 図を含む記事は `uv sync` 済みの環境でレンダーする(direnv 有効なら自動)。

## 2. プレビューで確認する

```bash
uv run quarto preview    # ホットリロード。VS Code ではプレビューボタン or ⌘+⇧+K
```

確認ポイント: レイアウト崩れ、数式の描画、light/dark 両テーマ、リスティングカードのサムネイル。

## 3. `_site/` をコミットする

このリポジトリは GitHub Actions デプロイを使わず、**ローカルレンダー結果の `_site/` をコミットして配信する**(独自ドメイン `serika.work`、`CNAME` + `.nojekyll`)。公開したい変更は、ソースと更新後の `_site/` を同じコミットに含める。

注意: autosync が5分ごとに `git add -A` で自動 commit するため、レンダー → 確認 → コミットは一続きで行う。`posts/report/` の PDF 出力を触った場合はレンダー後の生成物も確認する。
