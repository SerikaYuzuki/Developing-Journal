#!/usr/bin/env bash
set -euo pipefail

FROM='scale:1,extensions:[]'
TO='scale:1,extensions:["physics","mhchem"]'

if ! command -v perl >/dev/null 2>&1; then
  echo "パッチに必要な perl が見つかりません。" >&2
  exit 1
fi

directory_mtime() {
  if stat -f '%m' "$1" >/dev/null 2>&1; then
    stat -f '%m' "$1"
  else
    stat -c '%Y' "$1"
  fi
}

patch_extensions_dir() {
  local extensions_dir="$1"
  local latest_dir=""
  local latest_mtime=0
  local candidate
  local mtime

  while IFS= read -r -d '' candidate; do
    mtime="$(directory_mtime "$candidate")"
    if (( mtime > latest_mtime )); then
      latest_dir="$candidate"
      latest_mtime="$mtime"
    fi
  done < <(find "$extensions_dir" -maxdepth 1 -type d -name 'quarto.quarto-*' -print0)

  if [[ -z "$latest_dir" ]]; then
    return 2
  fi

  local target="$latest_dir/assets/www/editor/index.js"
  if [[ ! -f "$target" ]]; then
    echo "Visual Editor の JavaScript が見つかりません: $target" >&2
    return 1
  fi

  local patched_count
  patched_count="$({ FROM="$TO" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
  if [[ "$patched_count" == "1" ]]; then
    echo "パッチ適用済みです: $target"
    return 0
  fi

  local source_count
  source_count="$({ FROM="$FROM" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
  if [[ "$source_count" != "1" ]]; then
    echo "置換対象が1か所ではありません（検出数: $source_count）。拡張の実装変更を確認してください。" >&2
    echo "対象: $target" >&2
    return 1
  fi

  local backup="$target.before-physics-patch"
  if [[ ! -e "$backup" ]]; then
    cp "$target" "$backup"
  fi

  FROM="$FROM" TO="$TO" perl -0pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$target"

  patched_count="$({ FROM="$TO" perl -0ne '$n += () = /\Q$ENV{FROM}\E/g; END { print $n // 0 }' "$target"; })"
  if [[ "$patched_count" != "1" ]]; then
    cp "$backup" "$target"
    echo "パッチ後の検証に失敗したため、バックアップへ戻しました: $backup" >&2
    return 1
  fi

  echo "Quarto Visual Editor に physics / mhchem を追加しました。"
  echo "対象: $target"
}

if [[ -n "${VSCODE_EXTENSIONS_DIR:-}" ]]; then
  extension_roots=("$VSCODE_EXTENSIONS_DIR")
else
  extension_roots=(
    "$HOME/.vscode/extensions"
    "$HOME/.vscode-insiders/extensions"
  )
fi

found=0
failed=0
for extensions_dir in "${extension_roots[@]}"; do
  [[ -d "$extensions_dir" ]] || continue

  if patch_extensions_dir "$extensions_dir"; then
    found=1
  else
    status=$?
    if [[ "$status" != "2" ]]; then
      failed=1
    fi
  fi
done

if (( found == 0 )); then
  echo "Quarto VS Code 拡張が見つかりません。拡張をインストールしてから再実行してください。" >&2
  exit 1
fi

if (( failed != 0 )); then
  exit 1
fi

echo "VS Code が起動中なら Developer: Reload Window を一度実行してください。"
