# AGENTS.md

このリポジトリで作業する AI エージェント向けのガイドです。人間の読者にも役立ちます。

## プロジェクト概要

- **種類**: [Quarto](https://quarto.org) 製の個人ブログ／開発ジャーナル（サイトタイトル: 「芹香のブログ」）。
- **著者**: Serika Yuzuki。記事・コメント・コミットメッセージは基本的に **日本語**。
- **公開**: 静的サイトを `_site/` に出力し、`CNAME` で独自ドメインに配信（GitHub Pages のデプロイワークフローは使わない）。
- **言語環境**: Python は [`uv`](https://docs.astral.sh/uv/) で管理。`.venv/` はプロジェクトローカル。`direnv`（`.envrc`）で自動有効化。

## ディレクトリ構成

| パス | 役割 |
| --- | --- |
| `posts/` | 記事本体（`.qmd`）。カテゴリごとにサブディレクトリ。執筆規約は [`posts/AGENTS.md`](posts/AGENTS.md) を参照 |
| `_extensions/serika/` | 共有テーマ・フィルタ・テンプレート（glass テーマ、styles.css、ヘッダ差し込み、Lua フィルタ、CSL など）の vendoring 先。**源は [quarto-serika](https://github.com/SerikaYuzuki/quarto-serika)**（ローカル: `/Users/recky/GitHub/quarto-serika`）。直接編集せず、修正は quarto-serika 側で行い `scripts/install.sh <このプロジェクトのパス>` で取り込む |
| `bibliography.bib` | 文献データベース |
| `_templates/` | リスティングカードのテンプレート（EJS） |
| `_site/` | レンダー出力。**このリポジトリではコミット対象**（下記参照） |
| `_freeze/`, `.quarto/` | Quarto のキャッシュ。**コミットしない** |
| `scripts/` | `quarto` ラッパーと autosync（複数 Mac 同期）。詳細は [`scripts/AUTOSYNC.md`](scripts/AUTOSYNC.md) |
| `resource/` | 記事で参照する動画などのメディア |
| `.claude/skills/` | 定型作業スキルの実体（Claude Code では `/new-post` などで呼び出せる）。索引は [`SKILLS.md`](SKILLS.md) |

## セットアップ

初回のみ（各マシンで）:

```bash
uv python install
direnv allow
uv sync
python -m ipykernel install --user --name quarto-notes --display-name "Python (quarto-notes)"
./scripts/patch-quarto-visual-editor-mathjax.sh
```

最後のコマンドは、VS Code の Quarto Visual Editor で MathJax の `physics` / `mhchem` を使えるようにするローカルパッチ。Quarto 拡張を先にインストールしてから実行する。拡張更新後に数式プレビューが壊れた場合も同じコマンドを再実行し、VS Code が起動中なら「Developer: Reload Window」を一度実行する。

## よく使うコマンド

```bash
uv run quarto preview                 # ローカルプレビュー（ホットリロード）
uv run quarto render                  # サイト全体をレンダー
uv run quarto render posts/xxx/yyy.qmd  # 単一ファイルのみレンダー（index/navbar も追従更新される）
```

- VS Code の Quarto 拡張はラッパー `scripts/quarto` 経由で `uv` を使う（プレビューボタン含む）。設定変更後は「Developer: Reload Window」を実行。
- プレビューのホットキーは `⌘ + ⇧ + K`。

## コミット規約

- `_site/` は**コミットする**（このリポジトリはローカルレンダー結果を成果物として保存する運用）。ソース変更と一緒に更新された `_site/` をコミットすること。
- `.venv/`, `_freeze/`, `.quarto/`, Jupyter チェックポイント、各種キャッシュは**コミットしない**（`.gitignore` 済み）。
- コミットメッセージは日本語で、変更内容が分かる簡潔な形（例: `refactor:`, `feat:` などのプレフィックスは既存履歴に倣う）。

## ⚠️ autosync に関する注意

`scripts/autosync.sh` が launchd 経由で **5 分ごとに `main` を自動 commit / rebase / push** する。エージェントとして作業するときは:

- 中途半端な状態で長時間放置すると自動コミットに巻き込まれる。まとまった単位で作業する。
- rebase 競合や push 失敗時は `origin/autosave/<hostname>` へ退避される（ローカルは壊れない）。復旧手順は [`scripts/AUTOSYNC.md`](scripts/AUTOSYNC.md) を参照。
- 破壊的な履歴操作（force push・rebase など）は autosync と競合しうるので、ユーザーの明示的な指示がない限り行わない。

## 関連ドキュメント

- 記事執筆のルール → [`posts/AGENTS.md`](posts/AGENTS.md)
- 定型ワークフロー集（索引）→ [`SKILLS.md`](SKILLS.md)。実体は `.claude/skills/<name>/SKILL.md`
- プロジェクトの決定事項・注意点メモ → [`memory.md`](memory.md)。**作業開始時に必ず読むこと**
- 自動同期の仕組み → [`scripts/AUTOSYNC.md`](scripts/AUTOSYNC.md)

Claude Code はルートの `CLAUDE.md` 経由で `AGENTS.md` / `SKILLS.md` / `memory.md` をセッション開始時に自動読込する。
