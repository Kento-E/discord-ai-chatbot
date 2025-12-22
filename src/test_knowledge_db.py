"""
知識データベース機能のテスト
"""

import os
import tempfile
import unittest
from datetime import datetime

from knowledge_db import KnowledgeDB


class TestKnowledgeDB(unittest.TestCase):
    """KnowledgeDBクラスのテスト"""

    def setUp(self):
        """各テスト前の準備"""
        # 一時ファイルでテスト用データベースを作成
        self.temp_db = tempfile.NamedTemporaryFile(
            delete=False, suffix=".db"
        )
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = KnowledgeDB(self.db_path)

    def tearDown(self):
        """各テスト後のクリーンアップ"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_insert_message(self):
        """メッセージの挿入テスト"""
        message = {
            "id": 123456789,
            "channel_id": 111,
            "channel_name": "general",
            "author_id": 222,
            "author_name": "TestUser",
            "content": "テストメッセージ",
            "created_at": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp(),
        }

        # 新規挿入
        result = self.db.insert_message(message)
        self.assertTrue(result)

        # 重複挿入（スキップされる）
        result = self.db.insert_message(message)
        self.assertFalse(result)

        # メッセージ数の確認
        count = self.db.get_message_count()
        self.assertEqual(count, 1)

    def test_insert_messages_batch(self):
        """バッチ挿入のテスト"""
        messages = [
            {
                "id": i,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": f"メッセージ {i}",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
            }
            for i in range(100, 110)
        ]

        # 初回挿入
        inserted, skipped = self.db.insert_messages_batch(messages)
        self.assertEqual(inserted, 10)
        self.assertEqual(skipped, 0)

        # 再度挿入（全てスキップ）
        inserted, skipped = self.db.insert_messages_batch(messages)
        self.assertEqual(inserted, 0)
        self.assertEqual(skipped, 10)

    def test_message_metadata(self):
        """メタデータ付きメッセージのテスト"""
        message = {
            "id": 123456789,
            "channel_id": 111,
            "channel_name": "general",
            "author_id": 222,
            "author_name": "TestUser",
            "content": "重要なメッセージ",
            "created_at": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp(),
            "category": "important",
            "importance": 10,
        }

        self.db.insert_message(message)

        # メッセージ取得
        messages = self.db.get_all_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["category"], "important")
        self.assertEqual(messages[0]["importance"], 10)

    def test_update_message_metadata(self):
        """メタデータ更新のテスト"""
        message = {
            "id": 123456789,
            "channel_id": 111,
            "channel_name": "general",
            "author_id": 222,
            "author_name": "TestUser",
            "content": "テストメッセージ",
            "created_at": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp(),
        }

        self.db.insert_message(message)

        # メタデータ更新
        result = self.db.update_message_metadata(
            123456789, category="test", importance=5
        )
        self.assertTrue(result)

        # 更新確認
        messages = self.db.get_all_messages()
        self.assertEqual(messages[0]["category"], "test")
        self.assertEqual(messages[0]["importance"], 5)

    def test_get_messages_by_filter(self):
        """フィルタ付きメッセージ取得のテスト"""
        messages = [
            {
                "id": 1,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": "カテゴリA",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
                "category": "A",
                "importance": 5,
            },
            {
                "id": 2,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": "カテゴリB",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
                "category": "B",
                "importance": 10,
            },
            {
                "id": 3,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": "カテゴリA重要",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
                "category": "A",
                "importance": 8,
            },
        ]

        self.db.insert_messages_batch(messages)

        # カテゴリAのみ取得
        filtered = self.db.get_all_messages(category="A")
        self.assertEqual(len(filtered), 2)

        # 重要度7以上のみ取得
        filtered = self.db.get_all_messages(min_importance=7)
        self.assertEqual(len(filtered), 2)

        # カテゴリAかつ重要度7以上
        filtered = self.db.get_all_messages(category="A", min_importance=7)
        self.assertEqual(len(filtered), 1)

    def test_embedding_insertion(self):
        """埋め込み挿入のテスト"""
        # メッセージ挿入
        message = {
            "id": 123456789,
            "channel_id": 111,
            "channel_name": "general",
            "author_id": 222,
            "author_name": "TestUser",
            "content": "テストメッセージ",
            "created_at": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp(),
        }
        self.db.insert_message(message)

        # 埋め込み挿入
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = self.db.insert_embedding(123456789, embedding)
        self.assertTrue(result)

        # 重複挿入（スキップ）
        result = self.db.insert_embedding(123456789, embedding)
        self.assertFalse(result)

        # 埋め込み数の確認
        count = self.db.get_embedding_count()
        self.assertEqual(count, 1)

    def test_get_messages_without_embeddings(self):
        """埋め込み未生成メッセージ取得のテスト"""
        # 3つのメッセージを挿入
        messages = [
            {
                "id": i,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": f"メッセージ {i}",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
            }
            for i in range(1, 4)
        ]
        self.db.insert_messages_batch(messages)

        # 1つだけ埋め込みを生成
        self.db.insert_embedding(1, [0.1, 0.2, 0.3])

        # 埋め込み未生成のメッセージを取得
        without_embeddings = self.db.get_messages_without_embeddings()
        self.assertEqual(len(without_embeddings), 2)
        self.assertEqual(without_embeddings[0]["id"], 2)
        self.assertEqual(without_embeddings[1]["id"], 3)

    def test_get_all_embeddings(self):
        """全埋め込み取得のテスト"""
        # メッセージと埋め込みを挿入
        messages = [
            {
                "id": i,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": f"メッセージ {i}",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
                "category": "A" if i % 2 == 0 else "B",
            }
            for i in range(1, 4)
        ]
        self.db.insert_messages_batch(messages)

        for i in range(1, 4):
            self.db.insert_embedding(i, [float(i), float(i + 1)])

        # 全埋め込み取得
        texts, embeddings = self.db.get_all_embeddings()
        self.assertEqual(len(texts), 3)
        self.assertEqual(len(embeddings), 3)

        # カテゴリフィルタ
        texts, embeddings = self.db.get_all_embeddings(category="A")
        self.assertEqual(len(texts), 1)

    def test_incremental_update(self):
        """増分更新のテスト"""
        # 初回: 100メッセージ挿入
        messages_batch1 = [
            {
                "id": i,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": f"メッセージ {i}",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
            }
            for i in range(1, 101)
        ]
        inserted, skipped = self.db.insert_messages_batch(messages_batch1)
        self.assertEqual(inserted, 100)
        self.assertEqual(skipped, 0)

        # 2回目: 一部重複を含む150メッセージ挿入
        messages_batch2 = [
            {
                "id": i,
                "channel_id": 111,
                "channel_name": "general",
                "author_id": 222,
                "author_name": "TestUser",
                "content": f"メッセージ {i}",
                "created_at": datetime.now().isoformat(),
                "timestamp": datetime.now().timestamp(),
            }
            for i in range(50, 200)
        ]
        inserted, skipped = self.db.insert_messages_batch(messages_batch2)
        self.assertEqual(inserted, 99)  # 101-199が新規
        self.assertEqual(skipped, 51)  # 50-100が重複

        # 総数確認
        total = self.db.get_message_count()
        self.assertEqual(total, 199)  # 1-100 + 101-199


if __name__ == "__main__":
    unittest.main()
