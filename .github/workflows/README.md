# GitHub Actions ワークフロー

このディレクトリには、リポジトリの自動化を行うGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### 1. Auto Merge on Approval (`auto-merge.yml`)

#### 概要

PRが承認されたときに自動的にSquash and Mergeを実行するワークフローです。

#### トリガー条件

- イベント: `pull_request_review` (submitted)
- 条件: レビューが"Approved"状態である

#### 動作

1. PR情報を取得し、マージ可能かどうかを確認
2. PRのコミット作者を取得
3. 承認レビューの数を確認（最新のレビューのみをカウント）
4. **コミット作者以外**による1件以上の承認がある場合、Squash and Mergeを実行

#### 必要な権限

- `contents: write` - リポジトリへの書き込み
- `pull-requests: write` - PRの操作

#### 注意事項

- **重要**: コミット作者による承認は無効です
  - GitHub Copilot等のBotが作成したコミットの場合、そのBotによる承認は承認数にカウントされません
  - ブランチ保護ルールで「コミット作者以外による承認」が必須の場合、別のユーザーによる承認が必要です
- ブランチ保護ルールが設定されている場合、そのルールに従います
  - ルール違反の場合、わかりやすいエラーメッセージを表示します
- マージコンフリクトがある場合、マージは実行されません
- 承認が取り消された場合は実行されません

### 2. Auto Delete Branch on Merge (`auto-delete-branch.yml`)

#### 概要

PRがマージされた後、ソースブランチを自動的に削除するワークフローです。

#### トリガー条件

- イベント: `pull_request` (closed)
- 条件: PRがマージされた（`merged == true`）

#### 動作

1. マージされたPRのブランチ情報を取得
2. ソースブランチを削除

#### 必要な権限

- `contents: write` - リポジトリへの書き込み

#### 注意事項

- 保護ブランチは削除されません
- 既に削除されているブランチの場合、エラーは無視されます
- フォークからのPRの場合、元のリポジトリのブランチは削除されません

## 使用方法

これらのワークフローは自動的に実行されるため、特別な設定は不要です。

### 自動マージを無効にしたい場合

1. `.github/workflows/auto-merge.yml` を削除または無効化
2. または、PRにラベルを追加してスキップする条件を追加

### 自動ブランチ削除を無効にしたい場合

1. `.github/workflows/auto-delete-branch.yml` を削除または無効化
2. または、リポジトリ設定で「Automatically delete head branches」を有効化

## トラブルシューティング

### ワークフローが実行されない

- GitHub Actionsが有効になっているか確認
- リポジトリの権限設定を確認
- ワークフローファイルの構文エラーを確認

### マージが実行されない

**「Repository rule violations found」エラーが発生する場合:**

このエラーは、ブランチ保護ルールにより自動マージが拒否されたことを示します。

原因と対処法:

1. **コミット作者による承認の問題**
   - GitHub Copilot等のBotが作成したPRは、そのBotによる承認が無効です
   - **対処法**: コミット作者以外のユーザー（リポジトリのオーナーやコラボレーター）が承認してください

2. **ブランチ保護ルールの確認**
   - リポジトリ設定: `Settings > Branches > Branch protection rules`
   - 「Require approvals」の設定を確認
   - 「Dismiss stale pull request approvals when new commits are pushed」が有効になっているか確認

3. **その他の確認項目**
   - マージコンフリクトがないか確認
   - 必要な承認数が満たされているか確認
   - Status checksが成功しているか確認

### ブランチが削除されない

- ブランチが保護されていないか確認
- ワークフローの実行ログを確認
- リポジトリの権限設定を確認

## カスタマイズ

### 承認数の変更

`auto-merge.yml` の以下の行を変更：

```yaml
if: fromJSON(steps.check_approvals.outputs.result) >= 1
```

例: 2件以上の承認が必要な場合は `>= 2` に変更

### マージ方法の変更

`auto-merge.yml` の以下の行を変更：

```yaml
merge_method: 'squash'
```

選択肢: `squash`, `merge`, `rebase`
