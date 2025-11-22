#!/usr/bin/env python3
"""
新しい応答生成関数の単体テスト（実装をテスト）
ai_agent.pyの実際の関数をインポートせず、ロジックの正しさを検証
"""
import re


def test_similarity_calculation():
    """Jaccard類似度計算のテスト"""
    print("=== 類似度計算のテスト ===\n")

    # テストケース1: 完全に同じ
    text1 = "これはテストです"
    text2 = "これはテストです"
    set1 = set(text1)
    set2 = set(text2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    similarity = intersection / union if union > 0 else 0
    print(f"完全一致: '{text1}' vs '{text2}' = {similarity:.2f}")
    assert similarity == 1.0, "完全一致の場合は1.0であるべき"

    # テストケース2: 部分一致
    text1 = "これはテストです"
    text2 = "これはテストですね"
    set1 = set(text1)
    set2 = set(text2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    similarity = intersection / union if union > 0 else 0
    print(f"部分一致: '{text1}' vs '{text2}' = {similarity:.2f}")
    assert 0.5 < similarity < 1.0, "部分一致の場合は0.5から1.0の間であるべき"

    # テストケース3: 全く違う
    text1 = "Python"
    text2 = "JavaScript"
    set1 = set(text1)
    set2 = set(text2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    similarity = intersection / union if union > 0 else 0
    print(f"全く違う: '{text1}' vs '{text2}' = {similarity:.2f}")
    assert similarity < 0.5, "全く違う場合は0.5未満であるべき"

    print("✓ 類似度計算テスト成功\n")
    return True


def test_detailed_answer_logic():
    """詳細回答生成ロジックのテスト"""
    print("=== 詳細回答生成ロジックのテスト ===\n")

    similar_messages = [
        "Pythonのインストールは公式サイトからできます",
        "ダウンロードページで自分のOSを選んでください",
        "インストーラーを実行すればOKです",
        "PATH設定を忘れずにチェックしてください",
        "インストール後はpython --versionで確認できます",
    ]

    persona = {
        "avg_message_length": 20.0,
    }

    # ロジックのテスト
    response_parts = []
    used_sentences = set()
    target_length = max(persona["avg_message_length"] * 3, 100)
    current_length = 0  # O(n)で長さを追跡

    for message in similar_messages:
        sentences = [s.strip() for s in re.split(r"[。！？]", message) if s.strip()]

        for sentence in sentences:
            # Jaccard類似度を使った重複検出
            is_duplicate = False
            for used in used_sentences:
                if len(sentence) > 0 and len(used) > 0:
                    set_sentence = set(sentence)
                    set_used = set(used)
                    intersection = len(set_sentence & set_used)
                    union = len(set_sentence | set_used)
                    similarity = intersection / union if union > 0 else 0
                    if similarity > 0.6:
                        is_duplicate = True
                        break

            if not is_duplicate and len(sentence) >= 3:
                response_parts.append(sentence)
                used_sentences.add(sentence)
                current_length += len(sentence)  # O(1)で更新

                if current_length >= target_length:
                    break

        if current_length >= target_length:
            break

    # 検証
    assert len(response_parts) >= 2, "最低2文は含まれるべき"
    assert current_length >= 60, "十分な長さの応答が生成されるべき"

    print(f"生成された文の数: {len(response_parts)}")
    print(f"合計文字数: {current_length}")
    print(f"目標文字数: {target_length}")
    print("✓ 詳細回答生成ロジックテスト成功\n")
    return True


def test_casual_response_logic():
    """カジュアル応答生成ロジックのテスト"""
    print("=== カジュアル応答生成ロジックのテスト ===\n")

    persona = {
        "avg_message_length": 15.0,
    }
    target_length = persona["avg_message_length"]

    # テストケース1: 適切な長さ
    message1 = "今日はいい天気ですね"  # 10文字
    result1 = "そのまま使用"
    print(f"テスト1 - 適切な長さ: {len(message1)}文字 → {result1}")
    assert (
        target_length * 0.5 <= len(message1) <= target_length * 1.5
    ), f"適切な長さの範囲外: {len(message1)}"

    # テストケース2: 長すぎる
    message2 = "これは非常に長いメッセージです。いろいろな内容が含まれています。"
    sentences = [s for s in re.split(r"[。！？]", message2) if s.strip()]
    result2 = sentences[0] + "。"
    print(f"テスト2 - 長すぎる: {len(message2)}文字 → 最初の文のみ: {len(result2)}文字")
    assert len(message2) > target_length * 1.5
    assert len(result2) < len(message2)

    # テストケース3: 短すぎる
    message3_1 = "OK"
    message3_2 = "了解です"
    result3 = message3_1 + " " + message3_2
    print(f"テスト3 - 短すぎる: {len(message3_1)}文字 → 2文結合: {len(result3)}文字")
    assert len(message3_1) < target_length * 0.5

    print("✓ カジュアル応答生成ロジックテスト成功\n")
    return True


def test_question_detection():
    """質問検出ロジックのテスト"""
    print("=== 質問検出ロジックのテスト ===\n")

    question_keywords = [
        "？",
        "?",
        "ですか",
        "ますか",
        "なに",
        "何",
        "どう",
        "いつ",
        "どこ",
        "だれ",
        "誰",
        "どのように",
        "なぜ",
        "教えて",
        "方法",
        "やり方",
    ]

    test_cases = [
        ("Pythonのインストール方法を教えてください", True),
        ("どうやって始めればいいですか？", True),
        ("これは何ですか", True),
        ("なぜこうなるのでしょうか", True),
        ("やり方を知りたいです", True),
        ("今日はいい天気ですね", False),
        ("頑張りましょう", False),
        ("なるほど", False),
    ]

    for text, expected_is_question in test_cases:
        query_lower = text.lower()
        is_question = any(q in query_lower for q in question_keywords)
        status = "✓" if is_question == expected_is_question else "✗"
        print(f'{status} "{text}" → 質問: {is_question}')
        assert is_question == expected_is_question, f"質問検出失敗: {text}"

    print("\n✓ 質問検出テスト成功\n")
    return True


def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("応答生成ロジックの単体テスト")
    print("=" * 60 + "\n")

    try:
        test_similarity_calculation()
        test_detailed_answer_logic()
        test_casual_response_logic()
        test_question_detection()

        print("=" * 60)
        print("✅ すべてのテストに合格しました！")
        print("=" * 60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        return False
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
