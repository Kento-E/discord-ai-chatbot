# 使い方ガイド

## はじめに

このDiscord AI AgentBotは、Discordサーバーの過去メッセージを学習して質問に答えるBotです。

このガイドでは、「知識データが未生成です。まずメッセージ取得・整形を行ってください。」というメッセージが表示された場合の対処方法を説明します。

## 前提条件

1. **Discord Bot トークンの取得**
   - [Discord Developer Portal](https://discord.com/developers/applications)でBotを作成
   - Botトークンを取得

2. **必要なIntentsの有効化**
   - Discord Developer Portalの「Bot」セクションで以下を有効化：
     - MESSAGE CONTENT INTENT ✓
     - SERVER MEMBERS INTENT ✓
     - GUILDS INTENT ✓

3. **BotをDiscordサーバーに招待**
   - 必要な権限：
     - メッセージ履歴を読む
     - メッセージを送信
     - メッセージを読む

4. **サーバーIDの取得**
   - Discordで開発者モードを有効化
   - サーバーを右クリック → 「IDをコピー」

## 知識データ生成手順

### ステップ1: 環境変数の設定

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"
```

### ステップ2: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### ステップ3: メッセージの取得

```bash
python src/fetch_messages.py
```

**実行内容**：

- 指定したDiscordサーバーから過去のメッセージを取得
- 各チャンネルから最大1,000件のメッセージを取得
- Botのメッセージは除外
- `data/messages.json` に保存

**実行結果の例**：

```
===========================================================
Discord メッセージ取得スクリプト
===========================================================

🤖 Bot "YourBot#1234" としてログインしました

✅ ギルド "あなたのサーバー" に接続しました
📊 チャンネル数: 5

📝 チャンネル #general からメッセージを取得中...
   → 234件のメッセージを取得
📝 チャンネル #random からメッセージを取得中...
   → 156件のメッセージを取得
...

✅ 合計 500件のメッセージを取得しました
💾 メッセージを保存しました: /path/to/data/messages.json

===========================================================
✅ メッセージ取得が完了しました
===========================================================

次のステップ:
  1. python src/prepare_dataset.py を実行して埋め込みデータを生成
  2. python src/main.py を実行してBotを起動
```

### ステップ4: 埋め込みデータの生成

```bash
python src/prepare_dataset.py
```

**実行内容**：

- `data/messages.json` からメッセージを読み込み
- AI検索用の埋め込みベクトルを生成
- `data/embeddings.json` に保存

**実行結果の例**：

```
Batches: 100%|████████████| 16/16 [00:05<00:00,  3.12it/s]
500件のメッセージを埋め込み化し、/path/to/data/embeddings.json に保存しました。
```

### ステップ5: Botの起動

```bash
python src/main.py
```

**実行結果の例**：

```
Logged in as YourBot#1234
Bot is running and ready to answer.
```

## Botの使い方

Botが起動したら、Discordで以下のコマンドを使用できます：

### コマンド

1. **メンションで質問**

```
@YourBot Discord Botの作り方を教えて
```

2. **!askコマンド**

```
!ask Pythonのインストール方法は？
```

### 応答例

```
過去の類似メッセージ:
- Pythonは公式サイトからダウンロードできるよ
- pip install でパッケージをインストールできます
- Python 3.11以降を推奨します
```

## トラブルシューティング

### メッセージが1件も取得できない場合

**考えられる原因**：

1. Botがサーバーに参加していない
2. Botに「メッセージ履歴を読む」権限がない
3. Discord Developer PortalでIntentsが有効化されていない
4. チャンネルにメッセージが存在しない

**対処方法**：

1. BotをDiscordサーバーに再招待
2. Botの権限を確認
3. Discord Developer Portalで必要なIntentsを有効化
4. Bot再起動

### 認証エラーが発生する場合

```
❌ エラー: 認証に失敗しました
```

**対処方法**：

- `DISCORD_TOKEN` が正しいか確認
- トークンを再生成して再設定

### ギルドが見つからない場合

```
❌ エラー: 指定されたギルドが見つかりません
```

**対処方法**：

- `TARGET_GUILD_ID` が正しいか確認
- Botがそのサーバーに参加しているか確認

## GitHub Actions での実行

GitHub Actionsを使用してBotを実行する場合、事前にローカル環境で知識データを生成することをお勧めします。

理由：

- メッセージ取得は1回だけ実行すれば良い
- GitHub Actionsの実行時間を節約できる
- データの更新が必要なときだけ再実行

## データの更新

Discordサーバーに新しいメッセージが追加された場合、以下の手順でデータを更新できます：

```bash
# 1. 新しいメッセージを取得
python src/fetch_messages.py

# 2. 埋め込みデータを再生成
python src/prepare_dataset.py

# 3. Botを再起動
python src/main.py
```

## まとめ

1. **初回セットアップ**: 環境変数設定 → パッケージインストール
2. **知識データ生成**: メッセージ取得 → 埋め込み生成
3. **Bot起動**: main.py実行
4. **使用**: DiscordでBotに質問

質問や問題がある場合は、GitHubのIssuesでお気軽にお問い合わせください。
