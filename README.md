# Developing-Journal

[Quarto](https://quarto.org) 製の個人ブログ／開発ジャーナル。Python 環境は `uv` で管理する。

## 開発環境

各マシンに `uv`、`direnv`、Quarto をインストールする。Python の仮想環境はプロジェクト直下の `.venv/` に作成され、Git の管理対象外となる。

### 初回セットアップ

```bash
uv python install
direnv allow
uv sync
python -m ipykernel install --user --name quarto-notes --display-name "Python (quarto-notes)"
./scripts/patch-quarto-visual-editor-mathjax.sh
```

最後のコマンドを実行する前に、VS Code の Quarto 拡張をインストールしておく。このパッチにより、Visual Editor で MathJax の `physics` / `mhchem` 拡張が使えるようになる。Quarto 拡張の更新後に数式プレビューが動かなくなった場合も同じコマンドを再実行する。パッチ適用時に VS Code が起動中なら、「Developer: Reload Window」を一度実行する。

仮想環境の保存先:

```bash
.venv/
```

`.venv/`、`_freeze/`、`.quarto/`、Jupyter のチェックポイント、各種ランタイム／キャッシュファイルはコミットしない。一方、このリポジトリでは `_site/` をコミット対象としているため、ローカルレンダーで更新された静的サイトはソース変更と一緒にコミットする。

### ローカルプレビュー

```bash
uv run quarto preview
```

VS Code の Quarto 拡張は `scripts/quarto` のラッパーを使うため、ツールバーの Preview ボタンも `uv` 経由で実行される。このラッパーは `QUARTO_PYTHON` に `uv` 管理の Python インタープリタを設定する。初めてこの設定を取り込んだときは、VS Code で「Developer: Reload Window」を実行する。

### ローカルレンダー

```bash
uv run quarto render
```

GitHub Pages のデプロイワークフローは使用していない。公開またはレンダー結果を保存するときは、更新された `_site/` もコミットする。

## 主な Python パッケージ

- `numpy`
- `pandas`
- `matplotlib`
- `plotly`
- `jupyter`
- `ipykernel`
