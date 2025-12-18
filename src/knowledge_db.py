"""
知識データベース管理モジュール

SQLiteを使用して知識データを管理します。
- メッセージの永続的な蓄積（上限なし）
- 増分更新対応（既存メッセージはスキップ）
- メタデータ管理（カテゴリ、重要度など）
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class KnowledgeDB:
    """知識データベース管理クラス"""

    def __init__(self, db_path: Optional[str] = None):
        """
        知識データベースを初期化

        Args:
            db_path: データベースファイルのパス（省略時はdata/knowledge.dbを使用）
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), "../data/knowledge.db"
            )
        self.db_path = db_path
        self._ensure_data_directory()
        self._init_database()

    def _ensure_data_directory(self):
        """dataディレクトリの存在を確認し、必要に応じて作成"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _init_database(self):
        """データベーステーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # メッセージテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
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
                )
            """)

            # 埋め込みテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    message_id INTEGER PRIMARY KEY,
                    embedding_vector TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
            """)

            # インデックス作成（検索性能向上）
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_channel_id 
                ON messages(channel_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_category 
                ON messages(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_importance 
                ON messages(importance)
            """)

            conn.commit()

    def insert_message(self, message: Dict) -> bool:
        """
        メッセージを挿入（既存の場合はスキップ）

        Args:
            message: メッセージデータの辞書

        Returns:
            bool: 新規挿入された場合True、既存でスキップされた場合False
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 既存チェック
            cursor.execute("SELECT id FROM messages WHERE id = ?", (message["id"],))
            if cursor.fetchone() is not None:
                return False

            # 新規挿入
            cursor.execute(
                """
                INSERT INTO messages 
                (id, channel_id, channel_name, author_id, author_name, 
                 content, created_at, timestamp, category, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message["id"],
                    message["channel_id"],
                    message["channel_name"],
                    message["author_id"],
                    message["author_name"],
                    message["content"],
                    message["created_at"],
                    message["timestamp"],
                    message.get("category"),
                    message.get("importance", 0),
                ),
            )
            conn.commit()
            return True

    def insert_messages_batch(self, messages: List[Dict]) -> Tuple[int, int]:
        """
        複数のメッセージを一括挿入

        Args:
            messages: メッセージデータの辞書のリスト

        Returns:
            Tuple[int, int]: (新規挿入数, スキップ数)
        """
        inserted = 0
        skipped = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for message in messages:
                # 既存チェック
                cursor.execute(
                    "SELECT id FROM messages WHERE id = ?", (message["id"],)
                )
                if cursor.fetchone() is not None:
                    skipped += 1
                    continue

                # 新規挿入
                cursor.execute(
                    """
                    INSERT INTO messages 
                    (id, channel_id, channel_name, author_id, author_name, 
                     content, created_at, timestamp, category, importance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message["id"],
                        message["channel_id"],
                        message["channel_name"],
                        message["author_id"],
                        message["author_name"],
                        message["content"],
                        message["created_at"],
                        message["timestamp"],
                        message.get("category"),
                        message.get("importance", 0),
                    ),
                )
                inserted += 1

            conn.commit()

        return inserted, skipped

    def get_all_messages(
        self,
        category: Optional[str] = None,
        min_importance: Optional[int] = None,
    ) -> List[Dict]:
        """
        全メッセージを取得

        Args:
            category: カテゴリでフィルタ（省略時は全て）
            min_importance: 最小重要度でフィルタ（省略時は全て）

        Returns:
            メッセージデータの辞書のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM messages WHERE 1=1"
            params = []

            if category is not None:
                query += " AND category = ?"
                params.append(category)

            if min_importance is not None:
                query += " AND importance >= ?"
                params.append(min_importance)

            query += " ORDER BY timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_messages_without_embeddings(self) -> List[Dict]:
        """
        埋め込みが未生成のメッセージを取得

        Returns:
            メッセージデータの辞書のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT m.* FROM messages m
                LEFT JOIN embeddings e ON m.id = e.message_id
                WHERE e.message_id IS NULL
                ORDER BY m.timestamp ASC
                """
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def insert_embedding(self, message_id: int, embedding: List[float]) -> bool:
        """
        埋め込みベクトルを挿入

        Args:
            message_id: メッセージID
            embedding: 埋め込みベクトル

        Returns:
            bool: 新規挿入された場合True、既存でスキップされた場合False
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 既存チェック
            cursor.execute(
                "SELECT message_id FROM embeddings WHERE message_id = ?",
                (message_id,),
            )
            if cursor.fetchone() is not None:
                return False

            # 新規挿入
            cursor.execute(
                """
                INSERT INTO embeddings (message_id, embedding_vector)
                VALUES (?, ?)
                """,
                (message_id, json.dumps(embedding)),
            )
            conn.commit()
            return True

    def get_all_embeddings(
        self,
        category: Optional[str] = None,
        min_importance: Optional[int] = None,
    ) -> Tuple[List[str], List[List[float]]]:
        """
        全埋め込みデータを取得

        Args:
            category: カテゴリでフィルタ（省略時は全て）
            min_importance: 最小重要度でフィルタ（省略時は全て）

        Returns:
            Tuple[List[str], List[List[float]]]: (テキストリスト, 埋め込みリスト)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT m.content, e.embedding_vector 
                FROM messages m
                INNER JOIN embeddings e ON m.id = e.message_id
                WHERE 1=1
            """
            params = []

            if category is not None:
                query += " AND m.category = ?"
                params.append(category)

            if min_importance is not None:
                query += " AND m.importance >= ?"
                params.append(min_importance)

            query += " ORDER BY m.timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            texts = []
            embeddings = []
            for row in rows:
                texts.append(row["content"])
                embeddings.append(json.loads(row["embedding_vector"]))

            return texts, embeddings

    def get_message_count(self) -> int:
        """
        メッセージ総数を取得

        Returns:
            メッセージ総数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM messages")
            return cursor.fetchone()[0]

    def get_embedding_count(self) -> int:
        """
        埋め込み総数を取得

        Returns:
            埋め込み総数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            return cursor.fetchone()[0]

    def update_message_metadata(
        self,
        message_id: int,
        category: Optional[str] = None,
        importance: Optional[int] = None,
    ) -> bool:
        """
        メッセージのメタデータを更新

        Args:
            message_id: メッセージID
            category: カテゴリ
            importance: 重要度

        Returns:
            bool: 更新された場合True、存在しない場合False
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 存在チェック
            cursor.execute("SELECT id FROM messages WHERE id = ?", (message_id,))
            if cursor.fetchone() is None:
                return False

            # 更新
            updates = []
            params = []

            if category is not None:
                updates.append("category = ?")
                params.append(category)

            if importance is not None:
                updates.append("importance = ?")
                params.append(importance)

            if not updates:
                return True

            params.append(message_id)
            query = f"UPDATE messages SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

            return True

    def close(self):
        """データベース接続を閉じる（通常は不要: context managerを使用）"""
        pass


# テスト用
if __name__ == "__main__":
    # テストデータベース作成
    test_db_path = "/tmp/test_knowledge.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = KnowledgeDB(test_db_path)

    # テストメッセージ挿入
    test_message = {
        "id": 123456789,
        "channel_id": 111,
        "channel_name": "general",
        "author_id": 222,
        "author_name": "TestUser",
        "content": "これはテストメッセージです",
        "created_at": datetime.now().isoformat(),
        "timestamp": datetime.now().timestamp(),
        "category": "test",
        "importance": 5,
    }

    inserted = db.insert_message(test_message)
    print(f"メッセージ挿入: {inserted}")

    # 重複挿入テスト
    inserted = db.insert_message(test_message)
    print(f"重複挿入テスト: {inserted} (Falseが正常)")

    # メッセージ取得
    messages = db.get_all_messages()
    print(f"メッセージ総数: {len(messages)}")

    # クリーンアップ
    os.remove(test_db_path)
    print("テスト完了")
