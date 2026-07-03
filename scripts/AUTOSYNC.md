# リポジトリ自動同期 (autosync)

複数のMacから同じリポジトリを使うために、launchdで定期的に
`autosync.sh` を実行し、commit/push/pullを自動化する仕組み。
`scripts/` ごと別のリポジトリにコピーすればそのまま使える
（launchdラベル・ログ名・通知タイトルはリポジトリのディレクトリ名から自動導出される）。

## 仕組みの概要

`autosync.sh` は5分ごとに起動し、ローカルの変更を自動commitしたうえで
`origin/main` とrebaseし、問題がなければ`main`へpushする。
rebase競合やpush失敗など、自動では安全に解決できない状況になった場合は、
ローカルの状態を壊さずに `origin` の `autosave/<hostname>` ブランチへ
退避pushし、macOS通知で人間の介入を促す。

大まかなフロー:

```
ロック取得 (多重起動防止)
  → rebase/merge進行中 or ブランチがmainでない → 通知して終了
  → ローカル変更があれば commit (add -A)
  → git fetch origin (失敗=オフライン扱いで黙って終了)
  → git rebase origin/main
      成功 → ローカルが先行していれば push origin main
               失敗したら1回だけ fetch+rebase をリトライ
                 （リトライ中のfetch失敗はオフライン扱いで黙って終了）
                 → それでも失敗なら退避
      失敗(競合) → rebase --abort → 退避
  → 成功したら通知フラグをクリア
```

退避 (evacuate) = `git push --force origin main:refs/heads/autosave/<hostname -s>`。
ローカルの `main` ブランチはそのままの状態で残るため、データは失われない。

通知は「エピソード（理由）ごとに1回」。`.git/autosync-notified` フラグファイルに
通知した理由が記録され、同じ理由が続く間は再通知しない
（launchdが5分ごとに実行するため、競合を手動解決している最中や
featureブランチで意図的に作業している間に通知が連発しないようにする）。
理由が変わった場合は別エピソードとして再通知される。
退避push自体は通知の有無にかかわらず毎回実行され、退避内容は最新に保たれる。
同期に成功するとフラグは自動で削除される。

## インストール手順

```sh
cd /path/to/repo
./scripts/install-autosync.sh
```

- `~/Library/LaunchAgents/com.serikayuzuki.<リポジトリ名小文字>-autosync.plist` を生成し、
  `launchctl bootstrap` でロードする。
- 5分 (300秒) 間隔で実行され、ロード直後にも1回実行される (`RunAtLoad`)。
- 既にロード済みの場合は自動的に `bootout` してから再ロードするため、
  何度実行しても安全（冪等）。
- ログは `~/Library/Logs/<リポジトリ名小文字>-autosync.log` に出力される。

別のリポジトリパスを使う場合は引数で指定できる:

```sh
./scripts/install-autosync.sh /path/to/repo
```

## アンインストール手順

```sh
launchctl bootout gui/$(id -u)/com.serikayuzuki.<リポジトリ名小文字>-autosync
rm -f ~/Library/LaunchAgents/com.serikayuzuki.<リポジトリ名小文字>-autosync.plist
```

(例: このリポジトリなら `com.serikayuzuki.developing-journal-autosync`)

## 競合時の復旧手順

macOSの通知で「競合のため autosave/\<hostname\> に退避しました」等が来たら:

1. リモートの退避ブランチとorigin/mainの差分を確認する。

   ```sh
   git fetch origin
   git log origin/main..origin/autosave/<hostname>
   git diff origin/main origin/autosave/<hostname>
   ```

2. ローカルの `main`（退避元マシン）で手動にmerge/rebaseして競合を解決する。

   ```sh
   git fetch origin
   git rebase origin/main
   # コンフリクトを手で解消 → git add → git rebase --continue
   ```

   もしくは、別マシン・別ワークツリーで `origin/autosave/<hostname>` を
   チェックアウトして解決してもよい。

3. 解決したら `main` を通常通りpushする。

   ```sh
   git push origin main
   ```

4. 不要になった退避ブランチをリモートから削除する。

   ```sh
   git push origin --delete autosave/<hostname>
   ```

5. 解決後に該当マシンで`autosync.sh`を一度手動実行し、
   `.git/autosync-notified` フラグが正しく消えて正常系に戻ることを確認する
   （自動同期が成功すればフラグは自動で削除される）。

## ログの場所

- launchd実行時の標準出力・標準エラー: `~/Library/Logs/<リポジトリ名小文字>-autosync.log`
- 手動実行時はターミナルの標準出力にそのまま日時付きで出力される。

## 手動実行・動作確認

```sh
./scripts/autosync.sh                       # デフォルト: このリポジトリを対象
./scripts/autosync.sh /path/to/other/repo   # 別リポジトリを対象にする場合
```

通知コマンドをテストしたい場合は `AUTOSYNC_NOTIFY_CMD` 環境変数で
差し替えられる（第1引数=タイトル、第2引数=本文で呼び出される）。

```sh
AUTOSYNC_NOTIFY_CMD=/path/to/stub.sh ./scripts/autosync.sh
```
