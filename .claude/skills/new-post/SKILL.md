---
name: new-post
description: 芹香のブログ (Developing-Journal) に新しい記事 (.qmd) を作成する。ブログ記事・技術メモ・AtCoder 記録・UE5 メモ・レポートなどを新規に書きたいときに使う。カテゴリの選択、テンプレート複製、frontmatter 規約を含む。
---

# 新しい記事の作成

詳細な執筆規約は [`posts/AGENTS.md`](../../../posts/AGENTS.md) を参照。以下はその実行手順。

## 1. カテゴリを決める

| ディレクトリ | 内容 |
| --- | --- |
| `posts/tech/` | 技術メモ・Tips |
| `posts/at_coder/` | 競技プログラミング (AtCoder) |
| `posts/卒業論文/` | 卒業論文関連 |
| `posts/ue5_aura_courses/`, `posts/ue5_project/` | Unreal Engine 5 |
| `posts/report/` | レポート (PDF 出力あり。`_metadata.yml` で lualatex + physics/mhchem) |
| `posts/play_ground/` | 試作・実験 |

新しいテーマなら新規サブディレクトリを作ってよい。数式・化学式を多用するレポートは `posts/report/` に置くと組版設定が効く。

## 2. テンプレートから作る

```bash
cp posts/play_ground/template.qmd "posts/<category>/<slug>.qmd"
```

frontmatter を埋め、`<!-- TODO: ... -->` コメントを削除する:

```yaml
---
title: "記事タイトル"
author: "Serika Yuzuki"
date: "2026-7-5"                  # YYYY-M-D 形式(日本ローカルの投稿日)
categories: [programming, 2026]   # ジャンル + 年 を併記する慣習
image: "images/thumbnail.webp"    # リスティングカードのサムネイル(省略可)
---
```

## 3. 本文を書く

- 日本語、口語まじりのカジュアルな一人称(既存記事のトーンに合わせる)。
- 見出しは `##` から始める(`#` はタイトルが担う)。
- コードは fenced code block。`code-fold`(「コードはこちら」)とコピー機能はサイト設定で有効。
- 画像は記事の近くの `images/` に置き相対パスで参照。

## 4. レンダーとコミット

```bash
uv run quarto render "posts/<category>/<slug>.qmd"   # index/sidebar も追従更新される
```

更新された `.qmd` と `_site/` をまとめてコミットする(`/render-check` 参照)。
