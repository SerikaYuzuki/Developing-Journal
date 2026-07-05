# SKILLS.md

このプロジェクトで繰り返し発生する定型作業の手順書(スキル)の索引。実体は `.claude/skills/<name>/SKILL.md` にあり、Claude Code では `/<name>` で呼び出せる。他のエージェントは該当ファイルを直接読んで手順に従うこと。前提はルートの [`AGENTS.md`](AGENTS.md) を参照。

| スキル | 用途 |
|---|---|
| [new-post](.claude/skills/new-post/SKILL.md) | 新しい記事 (.qmd) をテンプレートから正しいカテゴリ・frontmatter で作成する |
| [render-check](.claude/skills/render-check/SKILL.md) | 変更後のレンダー確認と `_site/` の更新・コミット |
| [autosync-recover](.claude/skills/autosync-recover/SKILL.md) | autosync の競合 (`autosave/<hostname>` 退避) からの復旧 |

## その他の小さな定型作業

### テーマ・スタイルを変更する

- 配色・テーマ: `_scss/theme-glass-dark.scss` / `_scss/theme-glass-light.scss`
- 汎用スタイル: `styles.css`
- HTML ヘッダへの差し込み: `_includes/`(plotly 設定・サイドバートグル)
- 変更後は `uv run quarto render` で全体を再ビルドして反映を確認。

### 環境を新しいマシンにセットアップする

手順はルート [`AGENTS.md`](AGENTS.md) の「セットアップ」を参照。autosync も使うなら `./scripts/install-autosync.sh`(launchd に5分間隔で登録。冪等)。

## スキルの追加方法

1. `.claude/skills/<name>/SKILL.md` を作成する。frontmatter に `name` と `description`(いつ使うかが分かる一文)を書く。
2. この索引の表に1行追加する。

繰り返し発生した作業・繰り返し受けた指摘は、スキル化するか [`memory.md`](memory.md) に記録して次回に引き継ぐ。
