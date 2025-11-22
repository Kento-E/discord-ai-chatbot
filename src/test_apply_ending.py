#!/usr/bin/env python3
"""
apply_common_ending関数のテスト
不要な語尾が付く問題を再現・検証するためのテスト
"""
import random
import re


def apply_common_ending(base_text, common_endings):
    """
    メッセージに共通の語尾を適用する（重複を避ける）
    注: このテストでは、ai_agent.pyの実装をコピーしています

    Args:
        base_text: 元のメッセージ
        common_endings: 適用可能な語尾のリスト

    Returns:
        語尾が適用されたメッセージ
    """
    if not common_endings:
        return base_text

    # 既存の文末句読点と絵文字を除去
    text_without_punct = re.sub(r"[。！？\s\U0001F300-\U0001F9FF]+$", "", base_text)

    # 完全な文末表現のパターン（丁寧語、過去形、断定形など）
    complete_endings = [
        r"ます$",
        r"です$",
        r"ました$",
        r"でした$",
        r"ません$",
        r"ないです$",
        r"ますね$",
        r"ですね$",
        r"ましょう$",
        r"でしょう$",
    ]

    # 既に完全な文末がある場合は、語尾を追加しない
    for pattern in complete_endings:
        if re.search(pattern, text_without_punct):
            return base_text

    # すべての語尾からランダムに選択
    common_ending = random.choice(common_endings)

    # common_endingから句読点を除いた部分を抽出
    ending_without_punct = re.sub(r"[。！？\s]+$", "", common_ending)
    if not ending_without_punct:
        # 純粋な句読点の語尾 - そのまま追加
        return text_without_punct + common_ending
    elif text_without_punct.endswith(ending_without_punct):
        # 既にこの語尾を持っている - 元のテキストを使用
        return base_text
    else:
        # 異なる語尾 - 置き換える
        return text_without_punct + common_ending


def test_apply_common_ending():
    """apply_common_ending関数のテスト"""
    print("=== apply_common_ending関数のテスト ===\n")

    # テストケース1: 完全な文末がある場合は語尾を追加しない
    print("テストケース1: 完全な文末がある場合")
    base_text1 = "よろしくお願いします"
    common_endings1 = ["ました", "です", "ます"]
    # 期待: 語尾を追加しない（既に完全な文末がある）
    result1 = apply_common_ending(base_text1, common_endings1)
    print(f"  入力: '{base_text1}'")
    print(f"  語尾リスト: {common_endings1}")
    print(f"  結果: '{result1}'")
    print(f"  期待: 語尾を追加しない")
    print()

    # テストケース2: 絵文字がある場合
    print("テストケース2: 絵文字がある場合")
    base_text2 = "よろしくお願いします🥺"
    common_endings2 = ["ました", "です", "ます"]
    result2 = apply_common_ending(base_text2, common_endings2)
    print(f"  入力: '{base_text2}'")
    print(f"  語尾リスト: {common_endings2}")
    print(f"  結果: '{result2}'")
    print(f"  期待: 語尾を追加しない（既に完全な文末がある）")
    print()

    # テストケース3: 不完全な文末の場合は語尾を追加
    print("テストケース3: 不完全な文末の場合")
    base_text3 = "よろしくね"
    common_endings3 = ["ね。", "よ。", "です。"]
    result3 = apply_common_ending(base_text3, common_endings3)
    print(f"  入力: '{base_text3}'")
    print(f"  語尾リスト: {common_endings3}")
    print(f"  結果: '{result3}'")
    print(f"  期待: 適切な語尾を追加（または既に「ね」で終わっている場合は元のまま）")
    print()

    # テストケース4: 句読点がある場合
    print("テストケース4: 既に句読点がある場合")
    base_text4 = "よろしくお願いします。"
    common_endings4 = ["ました", "です", "ます"]
    result4 = apply_common_ending(base_text4, common_endings4)
    print(f"  入力: '{base_text4}'")
    print(f"  語尾リスト: {common_endings4}")
    print(f"  結果: '{result4}'")
    print(f"  期待: 語尾を追加しない")
    print()

    # 問題のケース再現テスト
    print("=" * 60)
    print("問題のケース再現テスト")
    print("=" * 60)
    print("\nシナリオ: ユーザーが「よろしくね」と送信")
    print("Bot応答: 「よろしくおねがいします よろしくお願いします🥺」")
    print("問題: この応答に「ました」が追加されて「よろしくおねがいします よろしくお願いします🥺ました」となる")
    print()

    # この問題を再現
    problematic_text = "よろしくおねがいします よろしくお願いします🥺"
    problematic_endings = ["ました", "です。", "ます。"]
    
    # 複数回実行して「ました」が選ばれた場合の動作を確認
    print(f"入力テキスト: '{problematic_text}'")
    print(f"語尾リスト: {problematic_endings}")
    print("\n10回実行した結果:")
    for i in range(10):
        random.seed(i)  # 再現性のためにシードを固定
        result = apply_common_ending(problematic_text, problematic_endings)
        print(f"  {i+1}. '{result}'")
    
    print("\n問題点: 「ました」が追加されるケースがある")
    print("期待: 既に完全な文末（「します」）があるので、語尾を追加しない")


def test_complete_endings():
    """完全な文末表現のテスト"""
    print("\n" + "=" * 60)
    print("完全な文末表現の網羅的テスト")
    print("=" * 60 + "\n")

    # 完全な文末を持つテストケース
    test_cases = [
        "よろしくお願いします",
        "ありがとうございます",
        "確認しました",
        "了解です",
        "わかりました",
        "そうでした",
        "できません",
        "わからないです",
        "いいですね",
        "頑張りましょう",
        "大丈夫でしょう",
        # 絵文字付き
        "よろしくお願いします🥺",
        "ありがとうございます😊",
        "了解です👍",
        # 句読点付き
        "よろしくお願いします。",
        "ありがとうございます！",
        "了解です？",
    ]

    common_endings = ["ました", "です", "ます", "ね。", "よ。"]

    print("完全な文末を持つケース（語尾を追加しない）:")
    all_passed = True
    for text in test_cases:
        result = apply_common_ending(text, common_endings)
        # 絵文字や句読点の有無を考慮して比較
        text_core = re.sub(r"[。！？\s\U0001F300-\U0001F9FF]+$", "", text)
        result_core = re.sub(r"[。！？\s\U0001F300-\U0001F9FF]+$", "", result)
        
        passed = text_core == result_core
        status = "✓" if passed else "✗"
        print(f"  {status} '{text}' → '{result}'")
        if not passed:
            all_passed = False

    # 不完全な文末を持つテストケース
    incomplete_cases = [
        "よろしくね",
        "ありがと",
        "わかった",
        "了解",
        "おけ",
    ]

    print("\n不完全な文末を持つケース（語尾の適用を評価）:")
    for text in incomplete_cases:
        result = apply_common_ending(text, common_endings)
        print(f"  '{text}' → '{result}'")

    if all_passed:
        print("\n✓ すべての完全な文末テストに合格しました")
    else:
        print("\n✗ 一部のテストが失敗しました")

    return all_passed


if __name__ == "__main__":
    test_apply_common_ending()
    test_complete_endings()
