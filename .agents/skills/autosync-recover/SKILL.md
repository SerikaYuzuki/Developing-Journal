---
name: autosync-recover
description: autosync の rebase 競合・push 失敗から復旧する。macOS 通知で「autosave/<hostname> に退避しました」が来たとき、または origin に autosave/* ブランチが残っているときに使う。
---

# autosync の競合からの復旧

仕組みの詳細は [`scripts/AUTOSYNC.md`](../../../scripts/AUTOSYNC.md) を参照。退避 = `main` の内容が `origin/autosave/<hostname>` へ force push された状態で、ローカルの `main` は壊れていない。

## 手順

1. 差分を確認する。

   ```bash
   git fetch origin
   git log origin/main..origin/autosave/<hostname>
   git diff origin/main origin/autosave/<hostname>
   ```

2. ローカル `main`(退避元マシン)で rebase して競合を解消する。

   ```bash
   git rebase origin/main
   # 競合を解消 → git add → git rebase --continue
   ```

3. 解決したら通常どおり push する。

   ```bash
   git push origin main
   ```

4. 退避ブランチをリモートから削除する。

   ```bash
   git push origin --delete autosave/<hostname>
   ```

5. `./scripts/autosync.sh` を一度手動実行し、`.git/autosync-notified` フラグが消えて正常系に戻ることを確認する。

## 注意

- 競合解消中も launchd が5分ごとに autosync を起動するが、rebase 進行中は検知して手を出さない(通知のみ)。
- ユーザーの明示的な指示なしに force push や履歴改変で「解決」しないこと。
