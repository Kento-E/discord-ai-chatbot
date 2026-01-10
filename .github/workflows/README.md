# GitHub Actions ワークフロー

このディレクトリには、リポジトリの自動化を行うGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### 1. 知識データのRelease自動アップロード (`upload-knowledge-to-release.yml`)

「知識データの生成と保存」ワークフローで作成された暗号化知識データを、GitHub Releaseとして自動的に公開するワークフローです。

詳細なアーキテクチャ、利点、使用方法、トラブルシューティングについては [docs/RELEASE_FLOW.md](../../docs/RELEASE_FLOW.md) を参照してください。

**トリガー**: `workflow_run` (「知識データの生成と保存」完了時)  
**権限**: `contents: write`

### 2. 知識データの生成と保存 (`generate-knowledge-data.yml`)

#### 概要

Discordサーバーからメッセージを取得し、AI学習用の埋め込みデータを生成して暗号化するワークフローです。生成されたデータは、GitHub Actionsのアーティファクトとして保存され、さらに「知識データのRelease自動アップロード」ワークフローによってReleaseとして公開されます。

#### トリガー条件

- 手動実行（`workflow_dispatch`）
- 定期実行（スケジュール設定は[ワークフローファイル](generate-knowledge-data.yml)を参照）

#### 動作

1. Discordサーバーからメッセージを取得
   - SQLiteデータベースに保存（増分更新対応）
   - 既存メッセージはスキップ
2. AI学習用の埋め込みデータを生成
   - 未生成メッセージのみ処理（増分更新）
3. データベースファイルを暗号化（AES-256-CBC）
4. アーティファクトとして保存（保持期間: 90日）

詳細は[データベース管理ガイド](../../docs/DATABASE.md)を参照してください。

#### 実行時間

- タイムアウト設定: 60分（[ワークフローファイル](generate-knowledge-data.yml)を参照）
- 想定実行時間: 30〜40分（データ量により変動）
  - メッセージ取得: 約12分
  - 埋め込みデータ生成: 約13分
  - 暗号化・アップロード: 約5分
  - その他セットアップ: 約4分

#### 必要な環境変数

- `DISCORD_TOKEN`: Discord Botのトークン
- `TARGET_GUILD_ID`: 取得対象のサーバーID
- `EXCLUDED_CHANNELS`: 除外するチャンネルのリスト（任意）
- `ENCRYPTION_KEY`: 暗号化に使用する鍵

### 3. Discord Botの実行 (`run-discord-bot.yml`)

#### 概要

Discord AIチャットボットBotを起動するワークフローです。最新のGitHub Releaseから暗号化された知識データをダウンロードし、復号化してBotを実行します。

#### トリガー条件

- 手動実行（`workflow_dispatch`）
  - 実行理由（任意）
  - 実行時間上限（オプション詳細は[ワークフローファイル](run-discord-bot.yml)を参照）

#### 動作

1. 最新の `knowledge-data-*` タグのReleaseを検索
2. Release assetから暗号化された知識データをダウンロード
3. 暗号化データを復号化
4. Discord Botを起動

#### 必要な環境変数

- `DISCORD_TOKEN`: Discord Botのトークン
- `TARGET_GUILD_ID`: 対象のサーバーID
- `ENCRYPTION_KEY`: 復号化に使用する鍵（生成時と同じ鍵）
- `GEMINI_API_KEY`: Google Gemini APIキー（応答生成に必須）
- `ADDITIONAL_CHATBOT_ROLE`（オプション）: チャットボットに追加したい役割や性格の指定。設定ファイルのベースプロンプトに加えて適用されます

#### 注意事項

- 実行時間の上限はワークフローの設定で選択可能（[ワークフローファイル](run-discord-bot.yml)を参照）
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

### 5. Dependabot Auto Approve (`dependabot-auto-approve.yml`)

#### 概要

Dependabotが作成したPRを自動的に承認し、マージ設定を有効化するワークフローです。Dependabotによる依存関係更新を完全自動化します。

#### 依存関係の自動更新について

このリポジトリではDependabotを使用して依存関係を自動的に監視し、更新が利用可能になるとPRを自動作成します。Python パッケージ（requirements.txt）と GitHub Actions ワークフローの両方を監視しています。

#### トリガー条件

- イベント: `pull_request_target` (opened, reopened, synchronize)
- 条件: PRの作成者が `dependabot[bot]` である

#### 動作

1. DependabotによるPRであることを確認（PRの作成者をチェック）
2. Dependabotメタデータを取得（更新タイプなど）
3. PRを自動承認（`gh pr review --approve`）
4. GitHub CLIの`gh pr merge --auto`コマンドで自動マージを有効化
5. すべてのステータスチェックが成功すると、GitHubが自動的にSquash and Mergeを実行
6. マージ後、ブランチが自動削除される

#### Dependabotの更新スケジュール

設定ファイル: [.github/dependabot.yml](../dependabot.yml)

- **実行タイミング**: 毎週土曜日午前9時（JST）
- **Python依存関係**: 最大10件のPRを同時にオープン
- **GitHub Actions**: 最大5件のPRを同時にオープン

#### ラベルとレビュアー

- 自動的に `dependencies` ラベルが付与される
- Python更新には `python` ラベル、GitHub Actions更新には `github-actions` ラベルが追加
- PRレビュアーとしてリポジトリオーナーが自動割り当て

#### セキュリティアップデート

- セキュリティ脆弱性が検出された場合、優先的に更新PRが作成される
- 手動でのバージョン管理作業を削減し、常に最新の安全な依存関係を維持

#### 自動承認とマージの動作フロー

1. Dependabotが依存関係の更新を検出
2. Dependabotが自動的にPRを作成
3. このワークフローがPRを自動承認
4. 同時に自動マージ設定を有効化（`--auto`フラグ）
5. 必須のステータスチェック（lintなど）が完了
6. → GitHubが自動的にSquash and Mergeを実行
7. → ブランチが自動削除される

#### 必要な権限

- `contents: write` - リポジトリへの書き込み
- `pull-requests: write` - PRの操作

#### 実装理由

`GITHUB_TOKEN`を使った承認では`pull_request_review`イベントがトリガーされないため、承認とマージ設定を同一ワークフローで実行する必要があります。`pull_request_target`イベントを使用することで、Dependabotのメタデータを安全に検証できます。

#### 注意事項

- ブランチ保護ルールで要求されるステータスチェックがすべて成功するまで、マージは実行されません
- セキュリティ上、`pull_request_target`イベントを使用しています
- Dependabotメタデータの検証により、正当なDependabot PRのみが処理されます

### 6. Auto Delete Branch on Merge (`auto-delete-branch.yml`)

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

### 7. Update Other PRs After Merge (`update-other-prs.yml`)

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

### 8. Secrets疎通テスト (`test-secrets.yml`)

#### 概要

Discord BotとGemini APIの認証情報（Secrets）の疎通を確認するワークフローです。DISCORD_TOKEN、TARGET_GUILD_ID、GEMINI_API_KEYの有効性を検証し、APIへの接続を確認します。

#### トリガー条件

- 手動実行（`workflow_dispatch`）
  - テストを実行する理由（任意）
  - 詳細情報を表示するかどうか（任意）
  - **Gemini API疎通テストを実行**（任意、デフォルト: false）
- mainブランチへのpush（対象ファイルが変更された場合のみ）
  - `.github/workflows/test-secrets.yml`
  - `src/test_connection.py`
  - `src/test_gemini_connection.py`

**注**: Gemini APIテストは無料枠を消費するため、手動実行時のみオプションで有効化できます。自動実行（push時）ではGemini APIテストはスキップされます。

#### 動作

1. Discord疎通テスト（常に実行）:
   - DISCORD_TOKENの有効性を確認
   - Discord APIへの接続を確認
   - TARGET_GUILD_IDで指定されたサーバーへのアクセスを確認
2. Gemini API疎通テスト（手動実行時のオプション）:
   - GEMINI_API_KEYの有効性を確認
   - Gemini APIへの接続を確認
   - Gemini APIを使用した応答生成が利用可能かを確認

#### 必要な環境変数

- `DISCORD_TOKEN`: Discord Botのトークン（必須）
- `TARGET_GUILD_ID`: 対象のサーバーID（必須）
- `GEMINI_API_KEY`: Google Gemini APIキー（オプション）

#### メリット

- APIキーの設定ミスを早期に発見
- 本番環境での実行前に疎通確認が可能
- Gemini APIを使用した応答生成の利用可否を事前に確認

#### 注意事項

- **自動実行時**: Discord疎通テストのみが実行されます。Gemini APIテストはスキップされます
- **手動実行時**: オプションでGemini API疎通テストを有効化できます（無料枠を消費します）
- GEMINI_API_KEYが設定されていない場合、テストはスキップされます
- 詳細情報表示オプションを有効にすると、Bot名やサーバー名がGitHub Actions Step Summaryに表示されます（リポジトリのActions権限を持つユーザーが閲覧可能）
- Gemini APIのテストでは最小限のトークン数でAPIリクエストを送信します（無料枠への影響を最小化）

### 9. Lint (`lint.yml`)

#### 概要

Pythonコードの品質チェックを行うワークフローです。コードフォーマット、スタイル、未使用変数などを自動的に検証します。

#### トリガー条件

- **Pull Request**: 以下のファイルが変更された場合
  - `**.py` - すべてのPythonファイル
  - `.github/workflows/lint.yml` - このワークフロー自体
  - `requirements.txt` - 依存関係ファイル
  - `pyproject.toml` - プロジェクト設定
  - `setup.cfg` - セットアップ設定
  - `.pre-commit-config.yaml` - pre-commit設定

- **Push to main**: 上記のファイルが変更された場合

#### 動作

1. Python 3.11をセットアップ
2. リンターをインストール（flake8, pylint, autoflake, isort, black）
3. 以下のチェックを実行：
   - **autoflake**: 未使用のimportと変数をチェック
   - **isort**: import文のソート順をチェック（blackプロファイル使用）
   - **black**: コードフォーマットをチェック
   - **flake8**: コードスタイルと構文エラーをチェック

#### 注意事項

- すべてのチェックは検証のみで、自動修正は行いません
- ローカルで修正する場合は、以下のコマンドを使用：
  ```bash
  # 全リンターを自動修正
  make format
  
  # またはpre-commitを使用
  pre-commit run --all-files
  ```
- pre-commitフックをインストールすると、コミット時に自動チェックされます
- ブランチ保護ルールの必須チェックに設定されている場合があります

## トラブルシューティング

### 自動マージが実行されない

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
