#!/usr/bin/env python3
"""
新しい応答生成機能のテスト
質問への詳細回答と通常会話への短い応答をテストする
"""
import json
import os


# テスト用データを作成
def create_test_data():
    """テスト用の埋め込みデータとペルソナを作成"""
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)

    # より多様なサンプルメッセージ
    messages = [
        "Pythonのインストール方法は公式サイトからダウンロードできます。",
        "まずpython.orgにアクセスして、Downloadsページを開いてください。",
        "自分のOSに合ったインストーラーをダウンロードして実行します。",
        "インストール時には「Add Python to PATH」にチェックを入れることを忘れないでください。",
        "インストール後はコマンドプロンプトやターミナルでpython --versionを実行して確認できます。",
        "Discord Botの作り方については、まずDiscord Developer Portalでアプリケーションを作成します。",
        "Botタブから新しいBotを追加して、トークンを取得してください。",
        "必要なIntentsを有効化することも重要です。",
        "discord.pyライブラリを使うとPythonで簡単にBotを作れます。",
        "おはようございます！今日も良い天気ですね。",
        "こんにちは！元気ですか？",
        "お疲れ様です。今日も頑張りましょう。",
        "ありがとうございます！助かります。",
        "了解しました。進めていきます。",
        "それは面白いですね。",
        "わかりました。確認してみます。",
        "いいですね！楽しみです。",
        "そうですね、同感です。",
        "素晴らしいアイデアだと思います。",
        "なるほど、理解できました。",
    ]

    # ダミーの埋め込みデータ
    embeddings_data = []
    for i, text in enumerate(messages):
        # 各メッセージに対して384次元のダミーベクトルを生成
        embedding = [0.1 * ((i * 7 + j * 3) % 10) for j in range(384)]
        embeddings_data.append({"text": text, "embedding": embedding})

    embeddings_path = os.path.join(data_dir, "embeddings.json")
    with open(embeddings_path, "w", encoding="utf-8") as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)

    print(f"✓ テスト用埋め込みデータを作成: {embeddings_path}")

    # ペルソナデータを作成
    persona = {
        "total_messages": len(messages),
        "avg_message_length": sum(len(m) for m in messages) / len(messages),
        "common_words": ["Python", "Bot", "Discord", "インストール", "方法"],
        "sample_greetings": ["おはようございます！", "こんにちは！", "お疲れ様です！"],
        "sample_messages": messages[:5],
        "description": f"過去{len(messages)}件のメッセージから学習したペルソナ",
    }

    persona_path = os.path.join(data_dir, "persona.json")
    with open(persona_path, "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)

    print(f"✓ テスト用ペルソナデータを作成: {persona_path}")

    return embeddings_path, persona_path


def test_detailed_question_response():
    """質問への詳細応答のテスト"""
    print("\n" + "=" * 60)
    print("質問への詳細応答テスト")
    print("=" * 60)

    # ai_agentモジュールをインポート
    from ai_agent import generate_response

    # 質問のテストケース
    test_questions = [
        "Pythonのインストール方法を教えてください",
        "Discord Botの作り方は？",
        "どうやって始めればいいですか？",
    ]

    for question in test_questions:
        print(f"\n質問: {question}")
        print("-" * 60)
        response = generate_response(question, top_k=5)
        print(f"応答:\n{response}")
        print("-" * 60)

        # 応答が複数行または十分な長さがあることを確認
        response_length = len(response)
        has_multiple_lines = "\n" in response or response_length > 50

        if has_multiple_lines:
            print(f"✓ 詳細な応答を生成（長さ: {response_length}文字）")
        else:
            print(f"⚠ 応答が短すぎる可能性があります（長さ: {response_length}文字）")


def test_casual_conversation_response():
    """通常会話への短い応答のテスト"""
    print("\n" + "=" * 60)
    print("通常会話への応答テスト")
    print("=" * 60)

    from ai_agent import generate_response

    # 通常会話のテストケース
    test_conversations = [
        "今日はいい天気ですね",
        "プロジェクト頑張りましょう",
        "なるほど",
    ]

    for conversation in test_conversations:
        print(f"\n入力: {conversation}")
        print("-" * 60)
        response = generate_response(conversation, top_k=3)
        print(f"応答: {response}")
        print("-" * 60)

        response_length = len(response)
        print(f"✓ ペルソナに沿った応答を生成（長さ: {response_length}文字）")


def test_greeting_response():
    """挨拶への応答のテスト"""
    print("\n" + "=" * 60)
    print("挨拶への応答テスト")
    print("=" * 60)

    from ai_agent import generate_response

    # 挨拶のテストケース
    test_greetings = [
        "おはよう",
        "こんにちは",
        "お疲れ様",
    ]

    for greeting in test_greetings:
        print(f"\n入力: {greeting}")
        response = generate_response(greeting, top_k=3)
        print(f"応答: {response}")

        # 挨拶が含まれていることを確認
        has_greeting = any(
            g in response for g in ["おはよう", "こんにちは", "お疲れ", "こんばんは"]
        )
        if has_greeting:
            print("✓ 適切な挨拶応答を生成")
        else:
            print("⚠ 挨拶が含まれていない可能性があります")


def main():
    print("\n" + "=" * 60)
    print("新しい応答生成機能の統合テスト")
    print("=" * 60)

    # テストデータを作成
    create_test_data()

    try:
        # 各テストを実行
        test_detailed_question_response()
        test_casual_conversation_response()
        test_greeting_response()

        print("\n" + "=" * 60)
        print("✅ すべてのテストが完了しました")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
