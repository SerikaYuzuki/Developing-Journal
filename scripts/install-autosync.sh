#!/usr/bin/env bash
#
# install-autosync.sh — リポジトリ用の launchd autosync エージェントをインストールする
# (ラベルとログ名はリポジトリのディレクトリ名から自動導出される)
#
# 使い方:
#   scripts/install-autosync.sh [REPO_DIR]
#
# REPO_DIR を省略した場合は、このスクリプトの親ディレクトリをリポジトリとして扱う。
#
# 何度実行しても安全（冪等）。既にロード済みのエージェントがあれば
# bootout してから新しい plist を bootstrap し直す。
#
# 注意: このスクリプトは launchctl を実行し、~/Library/LaunchAgents と
#       ~/Library/Logs に書き込む。実行前に内容を確認すること。

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUTOSYNC_SCRIPT="$SCRIPT_DIR/autosync.sh"

if [ "${1:-}" != "" ]; then
  REPO_DIR="$(cd "$1" && pwd)"
else
  REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

REPO_NAME_LOWER="$(basename "$REPO_DIR" | tr '[:upper:]' '[:lower:]')"
LABEL="com.serikayuzuki.${REPO_NAME_LOWER}-autosync"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs"
LOG_PATH="$LOG_DIR/${REPO_NAME_LOWER}-autosync.log"

if [ ! -x "$AUTOSYNC_SCRIPT" ]; then
  echo "ERROR: $AUTOSYNC_SCRIPT が存在しないか実行権限がありません。" >&2
  exit 1
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ERROR: $REPO_DIR はgitリポジトリではありません。" >&2
  exit 1
fi

mkdir -p "$PLIST_DIR"
mkdir -p "$LOG_DIR"

BASH_PATH="/bin/bash"

cat > "$PLIST_PATH" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${BASH_PATH}</string>
        <string>${AUTOSYNC_SCRIPT}</string>
        <string>${REPO_DIR}</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_PATH}</string>
    <key>StandardErrorPath</key>
    <string>${LOG_PATH}</string>
</dict>
</plist>
PLIST_EOF

echo "plist を書き出しました: $PLIST_PATH"

UID_NUM="$(id -u)"

# 既にロード済みなら一旦 bootout してから bootstrap し直す（冪等にするため）
launchctl bootout "gui/${UID_NUM}/${LABEL}" >/dev/null 2>&1 || true

if launchctl bootstrap "gui/${UID_NUM}" "$PLIST_PATH"; then
  echo "launchd エージェントをロードしました: ${LABEL}"
else
  echo "ERROR: launchctl bootstrap に失敗しました。" >&2
  exit 1
fi

echo "確認: launchctl print gui/${UID_NUM}/${LABEL}"
echo "アンインストール手順は scripts/AUTOSYNC.md を参照してください。"
