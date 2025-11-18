# GitHub Actions ワークフロー

このディレクトリには、リポジトリの自動化を行うGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### 1. 知識データのRelease自動アップロード (`upload-knowledge-to-release.yml`)

#### 概要

「知識データの生成と保存」ワークフローで作成された暗号化知識データを、GitHub Releaseとして自動的に公開するワークフローです。

詳細なアーキテクチャと利点については [docs/RELEASE_FLOW.md](../../docs/RELEASE_FLOW.md) を参照してください。

#### トリガー条件

- イベント: `workflow_run` (completed)
- 対象ワークフロー: 「知識データの生成と保存」
- 条件: 元のワークフローが成功した場合のみ実行

#### 動作

1. 「知識データの生成と保存」ワークフローが成功したことを確認
2. 暗号化された知識データ（`knowledge-data-encrypted` アーティファクト）をダウンロード
3. タイムスタンプ+ワークフロー実行IDベースのタグ名を生成
4. GitHub Releaseを作成し、暗号化データをアップロード
5. 古いReleaseを自動削除（最新5件のみ保持）

#### 必要な権限

- `contents: write` - Release作成とタグ操作

#### 注意事項

- 元のワークフローが失敗した場合は実行されません
- 最新5件より古いReleaseは自動的に削除されます
- `concurrency`設定により並行実行を制限

### 2. 知識データの生成と保存 (`generate-knowledge-data.yml`)

#### 概要

Discordサーバーからメッセージを取得し、AI学習用の埋め込みデータを生成して暗号化するワークフローです。生成されたデータは、GitHub Actionsのアーティファクトとして保存され、さらに「知識データのRelease自動アップロード」ワークフローによってReleaseとして公開されます。

#### トリガー条件

- 手動実行（`workflow_dispatch`）
- 定期実行（2ヶ月ごと）

#### 動作

1. Discordサーバーからメッセージを取得
2. AI学習用の埋め込みデータを生成
3. データを暗号化（AES-256-CBC）
4. アーティファクトとして保存（保持期間: 90日）

#### 必要な環境変数

- `DISCORD_TOKEN`: Discord Botのトークン
- `TARGET_GUILD_ID`: 取得対象のサーバーID
- `EXCLUDED_CHANNELS`: 除外するチャンネルのリスト（任意）
- `ENCRYPTION_KEY`: 暗号化に使用する鍵

### 3. Discord Botの実行 (`run-discord-bot.yml`)

#### 概要

Discord AIエージェントBotを起動するワークフローです。最新のGitHub Releaseから暗号化された知識データをダウンロードし、復号化してBotを実行します。

#### トリガー条件

- 手動実行（`workflow_dispatch`）
  - 実行理由（任意）
  - 実行時間上限（30分〜360分）

#### 動作

1. 最新の `knowledge-data-*` タグのReleaseを検索
2. Release assetから暗号化された知識データをダウンロード
3. 暗号化データを復号化
4. Discord Botを起動

#### 必要な環境変数

- `DISCORD_TOKEN`: Discord Botのトークン
- `TARGET_GUILD_ID`: 対象のサーバーID
- `ENCRYPTION_KEY`: 復号化に使用する鍵（生成時と同じ鍵）

#### 注意事項

- GitHub Actionsの制限により、最大6時間（360分）まで実行可能
- 知識データのReleaseが存在しない場合はエラーになります
- 「知識データの生成と保存」ワークフローを先に実行してください

### 4. Auto Merge on Approval (`auto-merge.yml`)

#### 概要

PRが承認されたときに、GitHubの自動マージ機能を有効化するワークフローです。承認とステータスチェックが完了すると、GitHubが自動的にSquash and Mergeを実行します。

#### トリガー条件

- イベント: `pull_request_review` (submitted)
- 条件: レビューが"Approved"状態である

#### 動作

1. PR情報を表示（PR番号、ブランチ、レビュアー）
2. PRがDraft状態でないことを確認
3. PRのマージ可能状態を確認
4. GitHub CLIの`gh pr merge --auto`コマンドで自動マージを有効化
5. ブランチ保護ルールで要求される承認とステータスチェックが完了すると、GitHubが自動的にSquash and Mergeを実行
6. マージ後、ブランチが自動削除される

#### 必要な権限

- `contents: write` - リポジトリへの書き込み
- `pull-requests: write` - PRの操作

#### GitHubの自動マージ機能について

このワークフローは、GitHub CLIを使用してGitHubの**ネイティブ自動マージ機能**を有効化します：

- **利点**:
  - シンプルで読みやすい実装（GitHub CLI使用）
  - ブランチ保護ルールと完全に互換性がある
  - 「Copilotとコラボレーションしたユーザー」の制約も正しく処理される
  - GitHub UIから自動マージのステータスが確認できる
  
- **動作フロー**:
  1. レビュアーがPRを承認する → ワークフローがトリガーされる
  2. ワークフローが自動マージを有効化（`gh pr merge --auto`）
  3. すべてのステータスチェックが成功
  4. → GitHubが自動的にSquash and Mergeを実行
  5. → ブランチが自動削除される

#### 注意事項

- ブランチ保護ルールで要求される承認とステータスチェックがすべて満たされるまで、マージは実行されません
- GitHub CLIを使用するため、シンプルで保守しやすい実装です
- Draft状態のPRは自動マージされません（Ready for reviewに変更してから承認してください）
- マージコンフリクトがある場合、自動マージは実行されません

### 5. Auto Delete Branch on Merge (`auto-delete-branch.yml`)

#### 概要

PRがマージされた後、ソースブランチを自動的に削除するワークフローです。

**注意**: `auto-merge.yml`ワークフローは既に`--delete-branch`オプションを使用してブランチを削除するため、このワークフローは**バックアップ**として機能します（手動マージされた場合など）。

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
- 既に削除されているブランチの場合、エラーは無視されます（auto-mergeで既に削除されている場合）
- フォークからのPRの場合、元のリポジトリのブランチは削除されません
- `auto-merge.yml`で自動マージされた場合、このワークフローは実行されますが、ブランチは既に削除されているため、無害なエラーが表示されます

### 6. Update Other PRs After Merge (`update-other-prs.yml`)

#### 概要

PRがmainブランチにマージされたときに、同じベースブランチを対象とする他のオープンなPRを自動的に更新するワークフローです。複数PRが起票されている場合の手動更新作業を削減できます。

#### トリガー条件

- イベント: `pull_request` (closed)
- ブランチ: `main`
- 条件: PRがマージされた（`merged == true`）

#### 動作

1. マージされたPR情報を表示
2. 同じベースブランチ（main）を対象とする他のオープンなPRを検索
3. 各PRに対して：
   - PRの詳細情報を取得（タイトル、ブランチ、マージ可能性など）
   - コンフリクトがある場合はスキップ
   - コンフリクトがない場合はGitHub APIの`update-branch`エンドポイントを使用してブランチを更新
4. 更新結果のサマリーを表示（成功、スキップ、失敗の件数）

#### 必要な権限

- `contents: write` - リポジトリへの書き込み
- `pull-requests: write` - PRの操作

#### メリット

- 複数PRが起票されている場合の手動更新作業を削減
- PRが常に最新のmainブランチと同期された状態を保つ
- コンフリクトの早期発見

#### 注意事項

- コンフリクトがあるPRは自動的にスキップされます
- エラーが発生しても処理は継続します（他のPRの更新を妨げない）
- mainブランチへのPRマージ時のみ動作します

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

### 自動マージが実行されない

**自動マージ機能が有効化されているのにマージされない場合:**

考えられる原因と確認項目:

1. **承認の不足**
   - ブランチ保護ルールで要求される承認数が満たされていない
   - PR画面の「Reviewers」セクションを確認
   - GitHub Copilot等のBotとコラボレーションしたユーザーによる承認は無効になる場合があります

2. **ステータスチェックの未完了**
   - 必要なステータスチェックが成功していない
   - PR画面の「Checks」タブを確認
   - すべての必須チェックが緑色（成功）になっている必要があります

3. **マージコンフリクト**
   - ベースブランチとコンフリクトがある
   - PR画面に「This branch has conflicts」と表示される
   - コンフリクトを解決する必要があります

4. **ブランチ保護ルールの制約**
   - リポジトリ設定: `Settings > Branches > Branch protection rules`
   - 「Require approvals」の設定を確認
   - 「Require status checks to pass」の設定を確認

**GitHubの自動マージ機能について:**

- PR画面で「Enable auto-merge」ボタンが表示されている場合、そのボタンをクリックして手動で有効化することもできます
- 自動マージが有効化されると、PR画面に「This pull request will auto-merge」と表示されます

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
