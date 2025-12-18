# 実装サマリー: 知識データの蓄積上限撤廃

## 概要

このPRは、Discord AI Agentの知識データ管理をJSONベースからSQLiteデータベースベースに移行し、メッセージ蓄積の上限を撤廃する機能を実装しました。

## 実装された機能

### 1. SQLiteデータベース管理システム

#### 新規ファイル: `src/knowledge_db.py`
- **KnowledgeDBクラス**: データベース操作のラッパー
- **メッセージテーブル**: 
  - 全メッセージ情報（ID、チャンネル、投稿者、内容）
  - メタデータ（カテゴリ、重要度）
- **埋め込みテーブル**: 
  - メッセージIDと埋め込みベクトルの紐付け
- **インデックス**: 検索パフォーマンス最適化

#### 主要機能
- `insert_message()`: メッセージの挿入（重複スキップ）
- `insert_messages_batch()`: 一括挿入（増分更新対応）
- `get_messages_without_embeddings()`: 未生成メッセージ取得
- `insert_embedding()`: 埋め込みベクトル挿入
- `get_all_embeddings()`: フィルタ付き埋め込み取得
- `update_message_metadata()`: メタデータ更新

### 2. メッセージ取得の強化

#### 更新ファイル: `src/fetch_messages.py`
- **上限撤廃**: `DEFAULT_MESSAGE_LIMIT = None`（全メッセージ取得）
- **データベース保存**: SQLiteへの直接保存
- **増分更新**: 既存メッセージIDをチェックしてスキップ
- **モード切り替え**: `USE_JSON_FALLBACK`環境変数でJSON形式にも対応

#### 実行フロー
```
1. データベース初期化
2. 既存メッセージ数を表示
3. Discordから全メッセージ取得
4. 新規メッセージのみ挿入
5. 統計情報を表示（新規/スキップ/累積）
```

### 3. 埋め込み生成の最適化

#### 更新ファイル: `src/prepare_dataset.py`
- **差分処理**: 埋め込み未生成のメッセージのみ処理
- **データベース保存**: 埋め込みをデータベースに直接保存
- **進捗表示**: 新規/既存/累積の件数を表示
- **モード切り替え**: JSON形式にも対応

#### 実行フロー
```
1. データベースから未生成メッセージ取得
2. 埋め込みモデルのロード
3. 未生成メッセージの埋め込み生成
4. データベースに保存
5. 統計情報を表示
```

### 4. AIエージェントの拡張

#### 更新ファイル: `src/ai_agent.py`
- **データベース対応**: SQLiteからデータ読み込み
- **自動モード検出**: DB/JSONの自動切り替え
- **フィルタリング準備**: メタデータによるフィルタリング基盤

### 5. ワークフローの更新

#### 更新ファイル: `.github/workflows/generate-knowledge-data.yml`
- **データベース暗号化**: SQLiteファイルの圧縮・暗号化
- **自動検出**: DB/JSONの自動判定

#### 更新ファイル: `.github/workflows/run-discord-bot.yml`
- **復号化対応**: データベースファイルの復号化
- **データ確認**: DB/JSONの存在確認

## テスト

### 新規ファイル: `src/test_knowledge_db.py`

全9テストが実装され、すべて合格:

1. **test_insert_message**: メッセージ挿入と重複チェック
2. **test_insert_messages_batch**: バッチ挿入
3. **test_message_metadata**: メタデータ付きメッセージ
4. **test_update_message_metadata**: メタデータ更新
5. **test_get_messages_by_filter**: フィルタ付き取得
6. **test_embedding_insertion**: 埋め込み挿入
7. **test_get_messages_without_embeddings**: 未生成メッセージ取得
8. **test_get_all_embeddings**: 全埋め込み取得
9. **test_incremental_update**: 増分更新の動作確認

## ドキュメント

### 更新されたドキュメント

1. **README.md**
   - 機能概要にDB管理機能を追加
   - データ保存先をSQLiteに更新
   - 増分更新の説明を追加

2. **docs/USAGE.md**
   - メッセージ取得の説明を更新
   - 埋め込み生成の説明を更新
   - 実行結果の例を更新

3. **.github/workflows/README.md**
   - ワークフローの動作説明を更新
   - データベースの利点を追加

### 新規ドキュメント

4. **docs/DATABASE.md**
   - 包括的なデータベース管理ガイド
   - スキーマ定義
   - 使用方法とサンプルコード
   - トラブルシューティング
   - パフォーマンス比較

## 技術的な詳細

### データベーススキーマ

```sql
-- メッセージテーブル
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    channel_name TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    timestamp REAL NOT NULL,
    category TEXT DEFAULT NULL,
    importance INTEGER DEFAULT 0,
    created_in_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 埋め込みテーブル
CREATE TABLE embeddings (
    message_id INTEGER PRIMARY KEY,
    embedding_vector TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

### 増分更新の仕組み

```python
# 既存メッセージIDをチェック
cursor.execute("SELECT id FROM messages WHERE id = ?", (message["id"],))
if cursor.fetchone() is not None:
    return False  # スキップ

# 新規メッセージのみ挿入
cursor.execute("INSERT INTO messages (...) VALUES (...)", ...)
return True  # 挿入成功
```

### 後方互換性

```python
# 自動モード検出
use_db = os.path.exists(DB_PATH) and not USE_JSON_FALLBACK

if use_db:
    # データベースモード
    db = KnowledgeDB(DB_PATH)
    texts, embeddings = db.get_all_embeddings()
else:
    # JSONモード（後方互換）
    with open(EMBED_PATH, "r") as f:
        dataset = json.load(f)
    texts = [item["text"] for item in dataset]
    embeddings = [item["embedding"] for item in dataset]
```

## パフォーマンス改善

### 初回実行
- メッセージ取得: 全チャンネルの全メッセージ
- 埋め込み生成: 全メッセージ

### 2回目以降
- メッセージ取得: **新規メッセージのみ**（既存はスキップ）
- 埋め込み生成: **未生成メッセージのみ**（既存は再利用）

### 具体例

| 実行 | メッセージ取得 | 埋め込み生成 | 時間節約 |
|------|--------------|------------|---------|
| 初回 | 500件 | 500件 | - |
| 2回目 | 50件（新規） | 50件（新規） | 約90% |

## セキュリティ

### CodeQLスキャン結果
- **Python**: 脆弱性なし
- **Actions**: 脆弱性なし

### データ保護
- データベースファイルは`.gitignore`で除外
- GitHub Releaseでは暗号化（AES-256-CBC）
- 暗号鍵はGitHub Secretsで管理

## 利点

### 1. 上限なしのメッセージ蓄積
- 従来: 各チャンネル最大10,000メッセージ
- 現在: 制限なし（ストレージ容量のみ）

### 2. 増分更新による高速化
- 2回目以降は新規メッセージのみ処理
- 実行時間を大幅に短縮

### 3. メタデータ管理
- カテゴリ分類
- 重要度の設定
- 将来的な拡張性

### 4. コストゼロ
- SQLiteファイルベース
- GitHub Actions無料枠内で動作
- 追加サービス不要

### 5. 後方互換性
- 既存のJSON形式もサポート
- 環境変数で切り替え可能
- 段階的な移行が可能

## 使用方法

### 初回実行

```bash
# メッセージ取得
export DISCORD_TOKEN="your_token"
export TARGET_GUILD_ID="your_guild_id"
python src/fetch_messages.py

# 埋め込み生成
python src/prepare_dataset.py

# Bot起動
python src/main.py
```

### 2回目以降（増分更新）

```bash
# 新規メッセージのみ取得
python src/fetch_messages.py

# 未生成埋め込みのみ生成
python src/prepare_dataset.py

# Bot起動
python src/main.py
```

### JSON形式に戻す場合

```bash
export USE_JSON_FALLBACK=true
python src/fetch_messages.py
python src/prepare_dataset.py
```

## まとめ

このPRにより、Discord AI Agentは以下を実現しました：

1. ✅ メッセージ蓄積の上限撤廃
2. ✅ 増分更新による高速化
3. ✅ メタデータ管理機能
4. ✅ GitHub Actions無料枠での利用
5. ✅ 後方互換性の維持
6. ✅ 包括的なテストとドキュメント
7. ✅ セキュリティチェック合格

すべての要件を満たし、テストは全て合格し、セキュリティ脆弱性もありません。
