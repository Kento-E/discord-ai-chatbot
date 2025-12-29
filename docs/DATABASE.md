# 知識データベース管理

## 概要

このプロジェクトは、SQLiteデータベースを使用して知識データを管理します。

## 主な機能

### 1. 上限なしのメッセージ蓄積

データベース方式では、メッセージの蓄積に上限がありません。古いメッセージも含めて全履歴を保持できます。

### 2. 増分更新

既存のメッセージIDをチェックし、新規メッセージのみを追加します。2回目以降の実行が高速になります。

### 3. メタデータ管理

各メッセージにカテゴリや重要度などの属性を付与できます。

#### 利用可能なメタデータ

| フィールド | 型 | 説明 | デフォルト |
|----------|------|------|----------|
| `category` | TEXT | カテゴリ分類 | NULL |
| `importance` | INTEGER | 重要度（0-10） | 0 |

#### メタデータの用途

- **カテゴリ**: メッセージの種類分け（例: "質問", "回答", "雑談"）
- **重要度**: 優先的に参照すべきメッセージの指定

### 4. GitHub Actions無料枠での利用

SQLiteはファイルベースのデータベースで、追加のサービス契約が不要です。GitHub Actionsで追加コストなしで利用できます。

## データベーススキーマ

### messagesテーブル

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,           -- Discord メッセージID
    channel_id INTEGER NOT NULL,      -- チャンネルID
    channel_name TEXT NOT NULL,       -- チャンネル名
    author_id INTEGER NOT NULL,       -- 投稿者ID
    author_name TEXT NOT NULL,        -- 投稿者名
    content TEXT NOT NULL,            -- メッセージ本文
    created_at TEXT NOT NULL,         -- 作成日時（ISO形式）
    timestamp REAL NOT NULL,          -- タイムスタンプ（Unix時間）
    category TEXT DEFAULT NULL,       -- カテゴリ（オプション）
    importance INTEGER DEFAULT 0,     -- 重要度（0-10、オプション）
    created_in_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- DB挿入日時
)
```

### embeddingsテーブル

```sql
CREATE TABLE embeddings (
    message_id INTEGER PRIMARY KEY,   -- メッセージID（外部キー）
    embedding_vector TEXT NOT NULL,   -- 埋め込みベクトル（テキスト形式でリストを保存）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 生成日時
    FOREIGN KEY (message_id) REFERENCES messages(id)
)
```

### インデックス

パフォーマンス向上のため、以下のインデックスが作成されます：

- `idx_messages_channel_id`: チャンネルIDでの検索
- `idx_messages_timestamp`: タイムスタンプでの検索
- `idx_messages_category`: カテゴリでの検索
- `idx_messages_importance`: 重要度での検索

## 使用方法

### 基本的な使い方

#### 1. メッセージの取得（初回）

```bash
export DISCORD_TOKEN="your_bot_token_here"
export TARGET_GUILD_ID="your_guild_id_here"
python src/fetch_messages.py
```

出力例:
```
📊 データベースモード: SQLite（増分更新対応）
   既存メッセージ数: 0件

🤖 Bot "YourBot#1234" としてログインしました
...
💾 データベースに保存中...
   新規追加: 500件
   既存スキップ: 0件
   累積総数: 500件
```

#### 2. 埋め込みデータの生成（初回）

```bash
python src/prepare_dataset.py
```

出力例:
```
📊 データベースモード: SQLite（増分更新）
   メッセージ総数: 500件
   既存埋め込み: 0件
   未生成メッセージ: 500件

🔄 500件のメッセージの埋め込みを生成中...
✅ 埋め込み生成完了

💾 データベースに保存中...
   新規追加: 500件
   累積総数: 500件
```

#### 3. メッセージの更新（2回目以降）

新しいメッセージが追加された後、再度実行：

```bash
python src/fetch_messages.py
python src/prepare_dataset.py
```

出力例:
```
📊 データベースモード: SQLite（増分更新対応）
   既存メッセージ数: 500件

💾 データベースに保存中...
   新規追加: 50件
   既存スキップ: 500件
   累積総数: 550件
```

### メタデータの活用

#### メタデータの設定

Pythonコードでメタデータを設定：

```python
from knowledge_db import KnowledgeDB

db = KnowledgeDB()

# メッセージ挿入時にメタデータを設定
message = {
    "id": 123456789,
    "channel_id": 111,
    "channel_name": "general",
    "author_id": 222,
    "author_name": "User",
    "content": "重要なお知らせ",
    "created_at": "2024-01-01T00:00:00",
    "timestamp": 1704067200.0,
    "category": "announcement",
    "importance": 10
}

db.insert_message(message)

# 既存メッセージのメタデータを更新
db.update_message_metadata(
    message_id=123456789,
    category="important",
    importance=9
)
```

#### メタデータによるフィルタリング

特定のカテゴリや重要度でメッセージを取得：

```python
from knowledge_db import KnowledgeDB

db = KnowledgeDB()

# カテゴリ「announcement」のメッセージのみ取得
announcements = db.get_all_messages(category="announcement")

# 重要度7以上のメッセージのみ取得
important_messages = db.get_all_messages(min_importance=7)

# カテゴリと重要度の組み合わせ
critical_announcements = db.get_all_messages(
    category="announcement",
    min_importance=9
)
```

埋め込みの取得時も同様にフィルタリング可能：

```python
# カテゴリ「technical」の埋め込みのみ取得
texts, embeddings = db.get_all_embeddings(category="technical")
```

## GitHub Actionsでの利用

### ワークフローの動作

1. **知識データの生成と保存**（`generate-knowledge-data.yml`）
   - メッセージ取得
   - 埋め込み生成
   - データベースファイルを暗号化
   - GitHub Releaseとして保存

2. **Discord Botの実行**（`run-discord-bot.yml`）
   - 最新Releaseをダウンロード
   - データベースファイルを復号化
   - Botを起動

### 暗号化・復号化

データベースファイルは既存の暗号化フローを使用：

```bash
# 暗号化
tar czf - data/knowledge.db | openssl enc -aes-256-cbc -salt -pbkdf2 \
  -pass env:ENCRYPTION_KEY -out knowledge-data.enc

# 復号化
openssl enc -aes-256-cbc -d -pbkdf2 -pass env:ENCRYPTION_KEY \
  -in knowledge-data.enc | tar xzf - -C ./
```

## トラブルシューティング

### データベースが見つからない

**症状**:
```
❌ エラー: 埋め込みデータが見つかりません: data/knowledge.db
```

**対処方法**:
1. `python src/fetch_messages.py` を実行
2. `python src/prepare_dataset.py` を実行

### 埋め込みが生成されない

**症状**: `prepare_dataset.py`を実行しても進捗がない

**原因**: 全メッセージに埋め込みが生成済み

**確認方法**:
```python
from knowledge_db import KnowledgeDB

db = KnowledgeDB()
print(f"メッセージ数: {db.get_message_count()}")
print(f"埋め込み数: {db.get_embedding_count()}")
```

## パフォーマンス

### 初回実行

- メッセージ取得: チャンネル数×メッセージ数に依存
- 埋め込み生成: メッセージ数に依存（数秒/100メッセージ）

### 2回目以降

- メッセージ取得: 新規メッセージ分のみ（大幅に高速化）
- 埋め込み生成: 新規メッセージ分のみ（大幅に高速化）

### 比較例

| 実行 | メッセージ取得 | 埋め込み生成 |
|------|--------------|------------|
| 初回 | 500件 | 500件 |
| 2回目 | 50件（新規のみ） | 50件（新規のみ） |

## セキュリティ

- データベースファイルは`.gitignore`で除外
- GitHub Releaseでは暗号化して保存
- `ENCRYPTION_KEY`はGitHub Secretsで管理

## 関連ファイル

- `src/knowledge_db.py`: データベース管理モジュール
- `src/fetch_messages.py`: メッセージ取得スクリプト
- `src/prepare_dataset.py`: 埋め込み生成スクリプト
- `src/ai_chatbot.py`: AIチャットボット（データベース対応）
- `src/test_knowledge_db.py`: データベース機能のテスト
