# Discord AI Chatbot

このプロジェクトは、Discordサーバーの過去メッセージを学習したAIチャットボットBotを無料で稼働させるアプリです。

LLM（Google Gemini API）を使用して、過去のメッセージを文脈として自然な返信を生成します。

## 機能概要

- Discord APIを使ったメッセージ取得
- データベースによる知識データ管理
- 取得メッセージのAI学習データ化
- **LLM API（Google Gemini）による高度な応答生成**
  - Google Gemini API対応（無料枠で利用可能）
  - 過去メッセージを文脈として活用
- Discord Botとして稼働

## クイックスタート

「知識データが未生成です」というエラーが表示された場合は、[詳細な使い方ガイド](docs/USAGE.md)をご覧ください。

## セットアップ

1. `requirements.txt`で依存パッケージをインストール

```bash
pip install -r requirements.txt
```

2. Pre-commitフックのセットアップ（開発者向け）

```bash
pre-commit install
```

これにより、コミット前に自動的にリンターが実行され、コード品質が保たれます。詳細は[リンターセットアップガイド](docs/LINTER_SETUP.md)を参照してください。

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
- 取得したメッセージをデータベースに保存

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

- メッセージデータから埋め込みベクトルを生成
- Sentence Transformerモデル（all-MiniLM-L6-v2）を使用
- 埋め込みデータをデータベースに保存

**注意**: 初回実行時はモデルのダウンロードに時間がかかる場合があります。

### 手順3: LLM APIの設定

Google Gemini APIキーを設定します。

```bash
export GEMINI_API_KEY="your_api_key_here"
```

詳細な設定手順については、[LLM API統合ガイド](docs/LLM_API_SETUP.md)をご覧ください。

### 手順4: Botの起動

知識データの生成とAPIキーの設定が完了したら、Botを起動できます。

```bash
python src/main.py
```

Botの使い方や応答の詳細については、[詳細な使い方ガイド](docs/USAGE.md#botの使い方)をご覧ください。

## ローカル環境での実行

以下の環境変数を設定してBotを実行します：

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"
export GEMINI_API_KEY="your_api_key_here"

# 1. メッセージ取得
python src/fetch_messages.py

# 2. 埋め込みデータ生成
python src/prepare_dataset.py

# 3. Bot起動
python src/main.py
```

**GEMINI_API_KEYの取得方法**: [LLM API統合ガイド](docs/LLM_API_SETUP.md)を参照してください。

### GitHub Actions上での実行

GitHub Actions上でDiscord Botを実行できます。

#### 1. GitHub Secretsの設定

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のSecretを追加：
   - `DISCORD_TOKEN`: Discord Botのトークン
   - `TARGET_GUILD_ID`: 取得対象のサーバーID
   - `ENCRYPTION_KEY`: 知識データの暗号化/復号化に使用する鍵（詳細: [.github/workflows/ENCRYPTION_KEY_SETUP.md](.github/workflows/ENCRYPTION_KEY_SETUP.md)）
   - `GEMINI_API_KEY`（オプション）: [LLM API統合ガイド](docs/LLM_API_SETUP.md)を参照
   - `ADDITIONAL_CHATBOT_ROLE`（オプション）: チャットボットに追加したい役割や性格の指定。設定ファイルのベースプロンプトに加えて適用されます

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

Discord TokenとGemini APIキーの有効性を確認するテストワークフローが用意されています。

手動でテストを実行する場合：

1. リポジトリの「Actions」タブを開く
2. 「Secrets疎通テスト」ワークフローを選択
3. 「Run workflow」ボタンをクリックして手動実行

詳細なトリガー条件、動作内容、注意事項については [.github/workflows/README.md](.github/workflows/README.md#7-secrets疎通テスト-test-secretsyml) を参照してください。

## GitHub Actions自動化機能

このリポジトリには、PR管理やブランチ管理を自動化するGitHub Actionsワークフローが含まれています。

詳細については、[.github/workflows/README.md](.github/workflows/README.md)を参照してください。

## MCP (Model Context Protocol) サポート

VS CodeでGitHub CopilotがMCP (Model Context Protocol)を通じてリポジトリ情報に直接アクセス可能にする機能を提供しています。

### 機能概要

GitHub、ファイルシステム、Pythonコード分析の3つのMCPサーバーを統合し、包括的な開発支援環境を構築します。

詳細な機能説明は [.vscode/README.md](.vscode/README.md#機能) を参照してください。

### クイックスタート

1. **前提条件**
   - VS Code（最新版推奨）
   - GitHub Copilot拡張機能
   - Docker（GitHub MCP Server用）
   - Node.js/npx（Filesystem MCP Server用）
   - uvx（Python Analyzer MCP Server用）

2. **使用方法**
   - VS Codeでこのリポジトリを開くと、GitHub Personal Access Tokenの入力を求められます
   - トークンの生成方法と詳細な設定手順は [.vscode/README.md](.vscode/README.md) を参照してください

### セキュリティ

Personal Access Tokenはプロンプト入力方式でリポジトリに保存されません。トークン生成方法と必要な権限スコープの詳細は [.vscode/README.md](.vscode/README.md#セキュリティ) を参照してください。

## コード品質とリンター

このプロジェクトでは、コード品質を保つためにリンターとフォーマッターを使用しています。

### 自動フォーマット

コミット時に自動的に以下が実行されます：

- **autoflake**: 未使用のimportと変数を削除
- **isort**: import文を整形
- **black**: コードスタイルを統一
- **flake8**: コード品質をチェック

### 手動実行

```bash
# リンターとフォーマッターを実行
make format

# チェックのみ（変更なし）
make check
```

詳細は[リンターセットアップガイド](docs/LINTER_SETUP.md)を参照してください。

## ディレクトリ構成

- src/: メインロジック
- data/: メッセージデータ保存
