#!/usr/bin/env bash
#
# autosync.sh — Developing-Journal リポジトリの自動commit/push/pull
#
# 使い方:
#   scripts/autosync.sh [REPO_DIR]
#
# REPO_DIR を省略した場合は、このスクリプトの親ディレクトリをリポジトリとして扱う。
#
# 環境変数:
#   AUTOSYNC_NOTIFY_CMD - 通知に使うコマンド。未設定時は osascript display notification。
#                         テスト時にスタブへ差し替えるために存在する。
#                         例: AUTOSYNC_NOTIFY_CMD='/path/to/stub.sh'
#
# 詳細な仕組みは scripts/AUTOSYNC.md を参照。

set -u

# ---- PATH は launchd 相当の最小構成を前提にする ----
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"

log() {
  printf '%s [autosync] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

notify() {
  local title="$1"
  local message="$2"
  if [ -n "${AUTOSYNC_NOTIFY_CMD:-}" ]; then
    "$AUTOSYNC_NOTIFY_CMD" "$title" "$message"
  else
    /usr/bin/osascript -e "display notification \"${message//\"/\\\"}\" with title \"${title//\"/\\\"}\""
  fi
}

# スパム防止つき通知。
# フラグファイル ($NOTIFIED_FLAG) に「理由キー」を記録し、
# 同じ理由が続く間は再通知しない（launchdが5分ごとに実行するため）。
# 理由が変わった場合は別エピソードとして通知し、フラグを上書きする。
# 同期成功時にフラグは削除される（＝次の失敗ではまた1回通知される）。
notify_once() {
  local reason_key="$1"
  local message="$2"
  if [ -f "$NOTIFIED_FLAG" ] && [ "$(cat "$NOTIFIED_FLAG")" = "$reason_key" ]; then
    log "already notified for reason '$reason_key'. skip notification."
    return 0
  fi
  notify "Developing-Journal autosync" "$message"
  printf '%s' "$reason_key" > "$NOTIFIED_FLAG"
}

# ---- リポジトリパスの決定 ----
if [ "${1:-}" != "" ]; then
  REPO_DIR="$1"
else
  REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  log "ERROR: $REPO_DIR is not a git repository (no .git directory). abort."
  exit 1
fi

HOSTNAME_SHORT="$(hostname -s)"
NOTIFIED_FLAG="$REPO_DIR/.git/autosync-notified"
LOCK_DIR="$REPO_DIR/.git/autosync.lock"

# ---- 多重起動防止 (mkdir方式のロック) ----
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  log "lock busy ($LOCK_DIR). another autosync is running. exit."
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT

log "=== autosync start (repo=$REPO_DIR host=$HOSTNAME_SHORT) ==="

# ---- rebase/merge 進行中チェック ----
if [ -d "$REPO_DIR/.git/rebase-merge" ] || [ -d "$REPO_DIR/.git/rebase-apply" ] || [ -f "$REPO_DIR/.git/MERGE_HEAD" ]; then
  log "rebase or merge already in progress. do nothing automatically."
  notify_once "rebase-in-progress" "rebase/mergeが進行中のため何もしませんでした。手動で解決してください。"
  exit 0
fi

# ---- ブランチチェック ----
CURRENT_BRANCH="$(git -C "$REPO_DIR" symbolic-ref --short -q HEAD || true)"
if [ "$CURRENT_BRANCH" != "main" ]; then
  log "current branch is not main (branch='${CURRENT_BRANCH:-DETACHED}'). do nothing."
  notify_once "not-on-main" "現在のブランチがmainではありません(${CURRENT_BRANCH:-detached HEAD})。自動同期をスキップしました。"
  exit 0
fi

# ---- 退避 (autosave) を行うヘルパー ----
# 退避pushは通知の有無にかかわらず毎回実行する（退避内容を最新に保つため）。
do_evacuate() {
  local reason="$1"
  log "evacuating local main to origin/autosave/$HOSTNAME_SHORT (reason: $reason)"
  if git -C "$REPO_DIR" push --force origin "main:refs/heads/autosave/$HOSTNAME_SHORT"; then
    log "evacuation push succeeded."
  else
    log "ERROR: evacuation push itself failed."
  fi

  notify_once "evacuate:$reason" "${reason}のため autosave/${HOSTNAME_SHORT} に退避しました。手動対応が必要です。"
}

# ---- ローカル変更のcommit ----
if [ -n "$(git -C "$REPO_DIR" status --porcelain)" ]; then
  log "local changes detected. committing."
  git -C "$REPO_DIR" add -A
  COMMIT_MSG="autosync: $HOSTNAME_SHORT $(date '+%Y-%m-%d %H:%M:%S')"
  if ! git -C "$REPO_DIR" commit -m "$COMMIT_MSG"; then
    log "ERROR: commit failed unexpectedly."
    exit 1
  fi
  log "committed: $COMMIT_MSG"
else
  log "no local changes."
fi

# ---- fetch ----
if ! git -C "$REPO_DIR" fetch origin; then
  log "fetch failed (likely offline). silently exit (offline is normal)."
  exit 0
fi

# ---- rebase ----
if ! git -C "$REPO_DIR" rebase origin/main; then
  log "rebase conflict detected. aborting rebase."
  git -C "$REPO_DIR" rebase --abort
  do_evacuate "リベース競合"
  exit 0
fi
log "rebase onto origin/main succeeded (or nothing to rebase)."

# ---- push (ローカルがoriginより先行していれば) ----
LOCAL_REV="$(git -C "$REPO_DIR" rev-parse main)"
REMOTE_REV="$(git -C "$REPO_DIR" rev-parse origin/main)"

if [ "$LOCAL_REV" = "$REMOTE_REV" ]; then
  log "local main is up to date with origin/main. nothing to push."
else
  log "local main is ahead of origin/main. pushing."
  if git -C "$REPO_DIR" push origin main; then
    log "push succeeded."
  else
    log "push failed. retrying once (fetch + rebase)."
    if ! git -C "$REPO_DIR" fetch origin; then
      # リトライ中のfetch失敗はオフライン正常系として扱い、黙って終了する
      # （オフラインなら退避pushも成功しないため）。次回実行時に再試行される。
      log "fetch failed during retry (likely offline). silently exit (offline is normal)."
      exit 0
    fi
    if git -C "$REPO_DIR" rebase origin/main; then
      if git -C "$REPO_DIR" push origin main; then
        log "push succeeded after retry."
      else
        log "push failed again after retry."
        do_evacuate "push失敗"
        exit 0
      fi
    else
      log "retry rebase failed (conflict)."
      git -C "$REPO_DIR" rebase --abort 2>/dev/null
      do_evacuate "push失敗後のリベース競合"
      exit 0
    fi
  fi
fi

# ---- 成功時: 通知フラグをクリア ----
if [ -f "$NOTIFIED_FLAG" ]; then
  log "clearing previous failure-notification flag."
  rm -f "$NOTIFIED_FLAG"
fi

log "=== autosync finished successfully ==="
exit 0
