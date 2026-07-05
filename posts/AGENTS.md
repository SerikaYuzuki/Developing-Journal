# posts/AGENTS.md

`posts/` 配下の記事（`.qmd`）を作成・編集するときのルール。全体方針はルートの [`AGENTS.md`](../AGENTS.md) を参照。

## ディレクトリとカテゴリ

記事はテーマごとのサブディレクトリに置く。既存の主なカテゴリ:

| ディレクトリ | 内容 |
| --- | --- |
| `posts/tech/` | 技術メモ・Tips |
| `posts/at_coder/` | 競技プログラミング（AtCoder） |
| `posts/卒業論文/` | 卒業論文関連 |
| `posts/ue5_aura_courses/`, `posts/ue5_project/` | Unreal Engine 5 |
| `posts/report/` | レポート（PDF 出力あり。`_metadata.yml` で lualatex 設定） |
| `posts/play_ground/` | 試作・実験 |

新しいテーマなら新規サブディレクトリを作ってよい。多くのディレクトリに `template.qmd` があるので、それを複製して書き始めるのが基本。

## Frontmatter 規約

各 `.qmd` の先頭に YAML を置く。既存記事に倣った標準形:

```yaml
---
title: "記事タイトル"
author: "Serika Yuzuki"
date: "2025-9-5"
categories: [programming, 2025]
image: "images/thumbnail.webp"   # サムネイル（外部 URL でも可）
---
```

- `date` は `YYYY-M-D` 形式（日本ローカルの投稿日）。
- `categories` はリスティングのフィルタに使われる。年（例: `2025`）とジャンルを併記する慣習。
- `image` はリスティングカードのサムネイル。省略可だが付けると見栄えが良い。

## 執筆スタイル

- **本文は日本語**。口語まじりのカジュアルな一人称の語り口（既存記事のトーンに合わせる）。
- 見出しは `##` から始める（`#` はタイトルが担うため本文では使わない）。
- コードは fenced code block（```` ```bash ````など）。サイト設定で `code-fold`（「コードはこちら」で折りたたみ）・コピー機能が有効。
- 数式・化学式を使う記事（特に `report/`）は `physics` / `mhchem` パッケージが `_metadata.yml` で読み込まれる。

## テンプレートから始める

```bash
cp posts/play_ground/template.qmd posts/<category>/<new-post>.qmd
```

テンプレートには `<!-- TODO: Title, Date を変更したのちにこのコメントを消してください -->` が入っている。編集後に TODO コメントを消すこと。

## レンダー

記事を書いたら単一ファイルレンダー（index / navbar / sidebar も自動更新される）:

```bash
uv run quarto render posts/<category>/<file>.qmd
# または
uv run quarto preview
```

更新された `_site/` をソースと一緒にコミットする（ルート [`AGENTS.md`](../AGENTS.md) のコミット規約参照）。
