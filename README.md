# Discord AI Agent

このプロジェクトは、Discordサーバーの過去メッセージを学習したAIエージェントBotを無料で稼働させるアプリです。

## 機能概要

- Discord APIを使ったメッセージ取得
- 取得メッセージのAI学習データ化
- 無料AIエージェントによる応答
- Discord Botとして稼働

## セットアップ

1. `requirements.txt`で依存パッケージをインストール
2. `config.json`でBotトークン等を設定
3. `main.py`を実行

## ディレクトリ構成

- src/: メインロジック
- data/: メッセージデータ保存

## 開発フロー

### PR自動化

このリポジトリでは、開発効率を向上させるためにPRワークフローが自動化されています：

- **自動マージ**: PRが承認されると自動的にSquash and Mergeが実行されます
- **自動ブランチ削除**: マージ後、ソースブランチが自動的に削除されます

詳細は [.github/workflows/README.md](.github/workflows/README.md) を参照してください。
