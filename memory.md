# memory.md

このプロジェクトの決定事項・非自明な注意点を記録するメモ。コードや git 履歴から自明なことは書かない。エージェントは作業前にここへ目を通し、新たに判明した重要事項は追記する。

更新ルール:

- 日付は相対表現(「先週」など)ではなく絶対日付 (YYYY-MM-DD) で書く。
- 解決した項目・古くなった項目は消す。肥大化させない。

## プロジェクトの決定事項

- **`_site/` はコミットする**。一般的な Quarto プロジェクトと異なり、GitHub Pages のデプロイワークフローを使わず、ローカルレンダー結果を成果物としてリポジトリに保存する運用。ソース変更時は `_site/` の更新も同じコミットに含める。
- **GitHub Actions のデプロイは削除済み**（コミット `4e38a50`）。CI での自動レンダー/デプロイは行わない。
- **配信は独自ドメイン**（`CNAME`）。`.nojekyll` を置いて Jekyll 処理を無効化。
- **Python 環境はプロジェクトローカルの `.venv/`**（コミット `92c7e32` で共有 venv から移行）。`uv` + `direnv` 前提。
- (2026-07-07) **共有テーマ・フィルタは quarto-serika に集約**。旧 `_scss/` `_includes/` `_filters/` `_csl/` `_reference-docs/` `styles.css` は削除し、`_extensions/serika/` に vendoring（源: https://github.com/SerikaYuzuki/quarto-serika 、ローカル `/Users/recky/GitHub/quarto-serika`）。修正は quarto-serika 側で行い、`/Users/recky/GitHub/quarto-serika/scripts/install.sh /Users/recky/GitHub/Developing-Journal` で取り込む。`quarto add <ローカルパス>` は `serika/` の org 階層をフラット化し、GitHub 経由の `quarto add SerikaYuzuki/quarto-serika` も `_extensions/SerikaYuzuki/` になるため使わない。html テーマはカスタム format ではなく `_quarto.yml` からのパス参照方式（navbar/sidebar 互換のため）。
- (2026-07-07) `posts/report/_metadata.yml` の `format.pdf` は quarto-serika の `report-pdf` format に**置き換えていない**（こちらは geometry・二段組・CSL 指定なしの簡易設定で、置き換えると出力レイアウトが変わるため）。統一するかはユーザー判断待ち。

## 注意点

- **autosync が 5 分ごとに `main` を自動 commit / push する**（launchd）。中途半端な状態での長時間放置や、ユーザー指示のない force push / 履歴改変は避ける。詳細と復旧手順は [`scripts/AUTOSYNC.md`](scripts/AUTOSYNC.md)。
- **記事・コミット・コメントは日本語**が基本。トーンはカジュアルな一人称。
- `report/` 配下は PDF 出力あり（`_metadata.yml` で lualatex + `physics` / `mhchem`）。数式・化学式記事はここに置くと組版設定が効く。
- (2026-07-14) **VS Code の Quarto Visual Editor で `physics` / `mhchem` を使うにはローカルパッチが必要**。Quarto 拡張 1.135.0 では Visual Editor が MathJax の `extensions: []` を固定指定しており、`quarto.mathjax.extensions` は反映されない。拡張更新後に `scripts/patch-quarto-visual-editor-mathjax.sh` を再実行し、VS Code が起動中なら一度だけ `Developer: Reload Window` を実行する。

## 未整理・TODO

- （随時追記）
