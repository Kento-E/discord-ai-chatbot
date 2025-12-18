"""
埋め込みデータ生成スクリプト

メッセージデータから埋め込みベクトルを生成します。
データベースモード: 未生成メッセージのみ処理（増分更新）
JSONモード: 全メッセージを処理（後方互換）
"""

import json
import os
import sys

from sentence_transformers import SentenceTransformer

from knowledge_db import KnowledgeDB

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/messages.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/knowledge.db")

USE_JSON_FALLBACK = os.environ.get("USE_JSON_FALLBACK", "false").lower() == "true"


def main():
    """メイン処理"""
    print("=" * 60)
    print("埋め込みデータ生成スクリプト")
    print("=" * 60)
    print()

    # データベースまたはJSONモード判定
    use_db = os.path.exists(DB_PATH) and not USE_JSON_FALLBACK

    if use_db:
        print("📊 データベースモード: SQLite（増分更新）")
        db = KnowledgeDB(DB_PATH)
        
        # 未生成メッセージを取得
        messages = db.get_messages_without_embeddings()
        total_messages = db.get_message_count()
        existing_embeddings = db.get_embedding_count()
        
        print(f"   メッセージ総数: {total_messages}件")
        print(f"   既存埋め込み: {existing_embeddings}件")
        print(f"   未生成メッセージ: {len(messages)}件")
        print()

        if len(messages) == 0:
            print("✅ 全てのメッセージに埋め込みが生成済みです")
            return

        # メッセージ本文のみ抽出
        texts = [msg["content"] for msg in messages if msg["content"].strip()]
        message_ids = [msg["id"] for msg in messages if msg["content"].strip()]

    else:
        print("📊 JSONモード（後方互換）")
        print()

        if not os.path.exists(DATA_PATH):
            print(f"❌ エラー: {DATA_PATH} が見つかりません")
            print("   先に python src/fetch_messages.py を実行してください")
            sys.exit(1)

        # メッセージデータの読み込み
        with open(DATA_PATH, "r") as f:
            messages = json.load(f)

        # メッセージ本文のみ抽出
        texts = [msg["content"] for msg in messages if msg["content"].strip()]
        print(f"   メッセージ総数: {len(texts)}件")
        print()

    # 埋め込みモデルのロード
    print("🔄 埋め込みモデルをロード中...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ モデルのロード完了")
    print()

    # 埋め込み生成
    print(f"🔄 {len(texts)}件のメッセージの埋め込みを生成中...")
    embeddings = model.encode(texts, show_progress_bar=True)
    print("✅ 埋め込み生成完了")
    print()

    # データベースまたはJSONに保存
    if use_db:
        # データベースに保存
        print("💾 データベースに保存中...")
        saved_count = 0
        for message_id, embedding in zip(message_ids, embeddings):
            if db.insert_embedding(message_id, embedding.tolist()):
                saved_count += 1
        
        total_embeddings = db.get_embedding_count()
        print(f"   新規追加: {saved_count}件")
        print(f"   累積総数: {total_embeddings}件")
        print()
        print(f"✅ データベースへの保存が完了しました: {DB_PATH}")
    else:
        # JSONファイルに保存
        output = [
            {"text": text, "embedding": emb.tolist()}
            for text, emb in zip(texts, embeddings)
        ]

        with open(OUTPUT_PATH, "w") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"💾 {len(output)}件の埋め込みを {OUTPUT_PATH} に保存しました")

    print()
    print("=" * 60)
    print("✅ 埋め込みデータ生成が完了しました")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("  python src/main.py を実行してBotを起動")
    print()


if __name__ == "__main__":
    main()
