# Discord AI Agent

このプロジェクトは、Discordサーバーの過去メッセージを学習したAIエージェントBotを無料で稼働させるアプリです。

## 機能概要

- Discord APIを使ったメッセージ取得
- 取得メッセージのAI学習データ化
- 無料AIエージェントによる応答
- Discord Botとして稼働

## セットアップ

1. `requirements.txt`で依存パッケージをインストール

```bash
pip install -r requirements.txt
```

2. 環境変数を設定

以下の環境変数を設定してください：

- `DISCORD_TOKEN`: Discord BotのトークンCHARACTER
- `TARGET_GUILD_ID`: 取得対象のサーバーID

### ローカル環境での実行

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"
python src/main.py
```

### GitHub Actions上での実行

GitHub Actions上でDiscord Botを実行できます。

#### 1. GitHub Secretsの設定

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のSecretを追加：
   - `DISCORD_TOKEN`: Discord BotのトークンCHARACTER
   - `TARGET_GUILD_ID`: 取得対象のサーバーID

#### 2. Discord Botの起動

1. リポジトリの「Actions」タブを開く
2. 「Discord Botの実行」ワークフローを選択
3. 「Run workflow」ボタンをクリック
4. 以下のオプションを設定：
   - **起動理由**（任意）：Botを起動する理由を入力
   - **実行時間の上限**：30分、60分、120分、180分、360分（6時間）から選択
5. 「Run workflow」をクリックして実行

**注意事項**：

- GitHub Actionsの制限により、最大6時間（360分）まで実行可能です
- タイムアウトに達すると自動的に停止します
- 継続的な稼働が必要な場合は、別途サーバーやクラウドサービスの利用を推奨します

#### 3. Secretsの疎通テスト

Secretsの有効性は以下のタイミングで自動的にテストされます：

- **mainブランチへのPR起票時**：PR作成時、更新時に自動実行
- **mainブランチへのpush時**：ワークフローファイル更新時に自動実行

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

## ディレクトリ構成

- src/: メインロジック
- data/: メッセージデータ保存
