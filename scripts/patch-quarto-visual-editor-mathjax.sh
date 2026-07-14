#!/usr/bin/env bash
set -euo pipefail

EXTENSIONS_DIR="${VSCODE_EXTENSIONS_DIR:-$HOME/.vscode/extensions}"
FROM='scale:1,extensions:[]'
TO='scale:1,extensions:["physics","mhchem"]'

if [[ ! -d "$EXTENSIONS_DIR" ]]; then
  echo "VS Code の拡張ディレクトリが見つかりません: $EXTENSIONS_DIR" >&2
  exit 1
fi

latest_dir=""
latest_mtime=0

while IFS= read -r -d '' candidate; do
  mtime="$(stat -f '%m' "$candidate")"
  if (( mtime > latest_mtime )); then
    latest_dir="$candidate"
    latest_mtime="$mtime"
  fi
done < <(find "$EXTENSIONS_DIR" -maxdepth 1 -type d -name 'quarto.quarto-*' -print0)

if [[ -z "$latest_dir" ]]; then
  echo "Quarto VS Code 拡張が見つかりません: $EXTENSIONS_DIR/quarto.quarto-*" >&2
  exit 1
fi

target="$latest_dir/assets/www/editor/index.js"
if [[ ! -f "$target" ]]; then
  echo "Visual Editor の JavaScript が見つかりません: $target" >&2
  exit 1
fi

patched_count="$({ FROM="$TO" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
if [[ "$patched_count" == "1" ]]; then
  echo "パッチ適用済みです: $target"
  exit 0
fi

source_count="$({ FROM="$FROM" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
if [[ "$source_count" != "1" ]]; then
  echo "置換対象が1か所ではありません（検出数: $source_count）。拡張の実装変更を確認してください。" >&2
  echo "対象: $target" >&2
  exit 1
fi

backup="$target.before-physics-patch"
if [[ ! -e "$backup" ]]; then
  cp "$target" "$backup"
fi

FROM="$FROM" TO="$TO" perl -0pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$target"

patched_count="$({ FROM="$TO" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
if [[ "$patched_count" != "1" ]]; then
  echo "パッチ後の検証に失敗しました。バックアップ: $backup" >&2
  exit 1
fi

echo "Quarto Visual Editor に physics / mhchem を追加しました。"
echo "対象: $target"
echo "VS Code が起動中なら Developer: Reload Window を一度実行してください。"
