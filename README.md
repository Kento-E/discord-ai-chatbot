# Discord AI Agent

このプロジェクトは、Discordサーバーの過去メッセージを学習したAIエージェントBotを無料で稼働させるアプリです。

## 機能概要

- Discord APIを使ったメッセージ取得
- 取得メッセージのAI学習データ化
- 無料AIエージェントによる応答
- Discord Botとして稼働

## クイックスタート

「知識データが未生成です」というエラーが表示された場合は、[詳細な使い方ガイド](docs/USAGE.md)をご覧ください。

## セットアップ

1. `requirements.txt`で依存パッケージをインストール

```bash
pip install -r requirements.txt
```

2. 環境変数を設定

以下の環境変数を設定してください：

- `DISCORD_TOKEN`: Discord Botのトークン
- `TARGET_GUILD_ID`: 取得対象のサーバーID

## 知識データの生成方法

Botを初めて使用する場合、または新しいメッセージを学習させたい場合は、以下の手順で知識データを生成してください。

### 手順1: メッセージの取得

Discordサーバーから過去のメッセージを取得します。

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"
python src/fetch_messages.py
```

このスクリプトは以下を実行します：

- 指定されたDiscordサーバーの全テキストチャンネルからメッセージを取得
- Botのメッセージを除外
- 取得したメッセージを `data/messages.json` に保存

**注意事項**：

- Botがサーバーに参加している必要があります
- Botに「メッセージ履歴を読む」権限が必要です
- Discord Developer Portalで以下のIntentsを有効化してください：
  - MESSAGE CONTENT INTENT
  - SERVER MEMBERS INTENT
  - GUILDS INTENT

### 手順2: 埋め込みデータの生成

取得したメッセージから、AI検索用の埋め込みデータを生成します。

```bash
python src/prepare_dataset.py
```

このスクリプトは以下を実行します：

- `data/messages.json` から メッセージを読み込み
- Sentence Transformerモデル（all-MiniLM-L6-v2）で埋め込みベクトルを生成
- 埋め込みデータを `data/embeddings.json` に保存

**注意**: 初回実行時はモデルのダウンロードに時間がかかる場合があります。

### 手順3: Botの起動

知識データの生成が完了したら、Botを起動できます。

```bash
python src/main.py
```

Botは以下のコマンドに応答します：

- `!ask <質問内容>`: 質問に関連する過去のメッセージを検索して返答
- `@Bot <質問内容>`: Botへのメンションでも同様に応答

### ローカル環境での実行

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"

# 1. メッセージ取得
python src/fetch_messages.py

# 2. 埋め込みデータ生成
python src/prepare_dataset.py

# 3. Bot起動
python src/main.py
```

### GitHub Actions上での実行

GitHub Actions上でDiscord Botを実行できます。

#### 1. GitHub Secretsの設定

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のSecretを追加：
   - `DISCORD_TOKEN`: Discord Botのトークン
   - `TARGET_GUILD_ID`: 取得対象のサーバーID
   - `ENCRYPTION_KEY`: 知識データの暗号化/復号化に使用する鍵（詳細: [.github/workflows/ENCRYPTION_KEY_SETUP.md](.github/workflows/ENCRYPTION_KEY_SETUP.md)）

#### 2. 知識データの生成

1. リポジトリの「Actions」タブを開く
2. 「知識データの生成と保存」ワークフローを選択
3. 「Run workflow」ボタンをクリックして実行
4. 完了後、自動的に知識データがGitHub Releaseとして公開されます

**知識データの保存について**：

- 生成された知識データは自動的にGitHub Releaseに保存されます
- タグ名: `knowledge-data-YYYYMMDD-HHMMSS-{workflow_run_id}` (UTC)
- 最新5件のReleaseが保持され、古いものは自動削除されます
- public リポジトリでは誰でもダウンロード可能です

#### 3. Discord Botの起動

1. リポジトリの「Actions」タブを開く
2. 「Discord Botの実行」ワークフローを選択
3. 「Run workflow」ボタンをクリック
4. 以下のオプションを設定：
   - **起動理由**（任意）：Botを起動する理由を入力
   - **実行時間の上限**：30分、60分、120分、180分、360分（6時間）から選択
5. 「Run workflow」をクリックして実行

**注意事項**：

- Botは最新のGitHub Releaseから知識データを自動的にダウンロードします
- 「知識データの生成と保存」を先に実行する必要があります
- GitHub Actionsの制限により、最大6時間（360分）まで実行可能です
- タイムアウトに達すると自動的に停止します
- 継続的な稼働が必要な場合は、別途サーバーやクラウドサービスの利用を推奨します

#### 4. Secretsの疎通テスト

Secretsの有効性は以下のタイミングで自動的にテストされます：

- **mainブランチへのpush時**：ワークフローファイル（`test-secrets.yml`）またはテストスクリプト（`test_connection.py`）の更新時に自動実行

手動でテストを実行する場合：

1. リポジトリの「Actions」タブを開く
2. 「Discord Secrets疎通テスト」ワークフローを選択
3. 「Run workflow」ボタンをクリックして手動実行

テストでは以下を確認します：

- DISCORD_TOKENの有効性
- Discord APIへの接続
- TARGET_GUILD_IDで指定されたサーバーへのアクセス

**注意**：このテストは読み取り専用の操作のみを実行し、
Discordサーバーへのメッセージ送信や通知は行いません。

## GitHub Actions自動化機能

このリポジトリには、PR管理やブランチ管理を自動化するGitHub Actionsワークフローが含まれています。

詳細については、[.github/workflows/README.md](.github/workflows/README.md)を参照してください。

## ディレクトリ構成

- src/: メインロジック
- data/: メッセージデータ保存
