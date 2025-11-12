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

### GitHub Secretsの設定（本番環境）

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のSecretを追加：
   - `DISCORD_TOKEN`: Discord BotのトークンCHARACTER
   - `TARGET_GUILD_ID`: 取得対象のサーバーID

3. `main.py`を実行

#### Secretsの疎通テスト

Secretsを更新した際は、GitHub Actionsで疎通テストを実行できます：

1. リポジトリの「Actions」タブを開く
2. 「Discord Secrets疎通テスト」ワークフローを選択
3. 「Run workflow」ボタンをクリックして手動実行

テストでは以下を確認します：

- DISCORD_TOKENの有効性
- Discord APIへの接続
- TARGET_GUILD_IDで指定されたサーバーへのアクセス

## ディレクトリ構成

- src/: メインロジック
- data/: メッセージデータ保存
