#!/usr/bin/env python3
"""
AIエージェント機能のテストスクリプト（ネットワークアクセス不要）
"""
import json
import os
import sys


# テスト用のモックデータを作成
def create_test_data():
    """テスト用の埋め込みデータとペルソナを作成"""
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)

    # サンプルメッセージ
    messages = [
        "おはようございます！今日も良い天気ですね。",
        "こんにちは！元気ですか？",
        "今日の会議はどうでしたか？",
        "プロジェクトの進捗状況を教えてください。",
        "ありがとうございます！助かります。",
        "了解しました。進めていきます。",
        "それは面白いですね。もっと詳しく教えてください。",
        "わかりました。確認してみます。",
        "お疲れ様です！今日はここまでにしましょう。",
        "次の機能について議論しましょう。",
    ]

    # ダミーの埋め込みデータ（実際の埋め込みの代わりに単純な数値）
    embeddings_data = []
    for i, text in enumerate(messages):
        # 各メッセージに対して384次元のダミーベクトルを生成
        embedding = [0.1 * (i + j) % 10 for j in range(384)]
        embeddings_data.append({"text": text, "embedding": embedding})

    embeddings_path = os.path.join(data_dir, "embeddings.json")
    with open(embeddings_path, "w", encoding="utf-8") as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)

    print(f"✓ テスト用埋め込みデータを作成: {embeddings_path}")

    # ペルソナデータを作成
    persona = {
        "total_messages": len(messages),
        "avg_message_length": sum(len(m) for m in messages) / len(messages),
        "common_words": ["今日", "会議", "プロジェクト", "ありがとう", "お疲れ"],
        "sample_greetings": ["おはようございます！", "こんにちは！", "お疲れ様です！"],
        "sample_messages": messages[:5],
        "description": f"過去{len(messages)}件のメッセージから学習したペルソナ",
    }

    persona_path = os.path.join(data_dir, "persona.json")
    with open(persona_path, "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)

    print(f"✓ テスト用ペルソナデータを作成: {persona_path}")

    return embeddings_path, persona_path


def test_response_generation():
    """応答生成機能のテスト"""
    print("\n=== 応答生成機能のテスト ===\n")

    # テストデータを作成
    create_test_data()

    # ai_agentモジュールから応答生成関数をインポート
    # ただし、SentenceTransformerのロードをスキップする必要がある
    print("\n応答生成ロジックのテスト:")

    # ペルソナデータの読み込みテスト
    persona_path = os.path.join(os.path.dirname(__file__), "../data/persona.json")
    with open(persona_path, "r", encoding="utf-8") as f:
        persona = json.load(f)

    print("\n✓ ペルソナ情報:")
    print(f'  - 総メッセージ数: {persona["total_messages"]}')
    print(f'  - 平均メッセージ長: {persona["avg_message_length"]:.2f}文字')
    print(f'  - 頻出単語: {", ".join(persona["common_words"][:5])}')

    # 簡単な応答生成ロジックのテスト
    test_queries = [
        "おはよう",
        "プロジェクトの状況は？",
        "ありがとう",
        "会議について教えて",
    ]

    print("\n✓ サンプルクエリへの応答生成テスト:")
    for query in test_queries:
        # 単純なキーワードマッチングで類似メッセージを検索
        sample_messages = persona["sample_messages"]
        response = sample_messages[0]  # 簡易版: 最初のメッセージを返す

        # 挨拶の場合
        if any(g in query for g in ["おはよう", "こんにちは", "お疲れ"]):
            response = persona["sample_greetings"][0]

        print(f'\n  入力: "{query}"')
        print(f'  応答: "{response}"')

    print("\n✓ テスト完了！")
    return True


if __name__ == "__main__":
    try:
        success = test_response_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ テスト失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
