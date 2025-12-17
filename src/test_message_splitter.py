#!/usr/bin/env python3
"""
message_splitter.pyのテスト
"""
import sys

from message_splitter import DISCORD_MAX_LENGTH, split_message


def test_short_message():
    """短いメッセージはそのまま返されることを確認"""
    print("=== test_short_message ===")
    message = "これは短いメッセージです。"
    result = split_message(message)

    assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
    assert result[0] == message, "Message should be unchanged"
    print("✓ 短いメッセージはそのまま返される")
    return True


def test_empty_message():
    """空のメッセージの処理を確認"""
    print("\n=== test_empty_message ===")
    result = split_message("")

    assert len(result) == 0, f"Expected empty list, got {result}"
    print("✓ 空のメッセージは空リストを返す")
    return True


def test_exact_limit_message():
    """ちょうど2000文字のメッセージの処理を確認"""
    print("\n=== test_exact_limit_message ===")
    message = "あ" * DISCORD_MAX_LENGTH
    result = split_message(message)

    assert len(result) == 1, f"Expected 1 chunk, got {len(result)}"
    assert len(result[0]) == DISCORD_MAX_LENGTH
    print("✓ ちょうど2000文字のメッセージは1つのチャンクになる")
    return True


def test_long_message_split():
    """2000文字を超えるメッセージが分割されることを確認"""
    print("\n=== test_long_message_split ===")
    # 2500文字のメッセージ
    message = "あ" * 2500
    result = split_message(message)

    assert len(result) == 2, f"Expected 2 chunks, got {len(result)}"
    assert all(len(chunk) <= DISCORD_MAX_LENGTH for chunk in result)
    assert (
        "".join(result) == message
    ), "Split chunks should reconstruct original message"
    print(f"✓ 2500文字のメッセージが{len(result)}つのチャンクに分割される")
    print(f"  チャンク1: {len(result[0])}文字")
    print(f"  チャンク2: {len(result[1])}文字")
    return True


def test_newline_split():
    """改行位置で分割されることを確認"""
    print("\n=== test_newline_split ===")
    # 改行を含む長いメッセージ
    line1 = "あ" * 1000
    line2 = "い" * 1000
    line3 = "う" * 500
    message = f"{line1}\n{line2}\n{line3}"

    result = split_message(message)

    assert len(result) >= 2, f"Expected at least 2 chunks, got {len(result)}"
    assert all(len(chunk) <= DISCORD_MAX_LENGTH for chunk in result)
    # 最初のチャンクは改行で終わるはず
    assert result[0].endswith("\n"), "First chunk should end with newline"
    print(f"✓ 改行を含むメッセージが{len(result)}つのチャンクに分割される")
    for i, chunk in enumerate(result, 1):
        print(f"  チャンク{i}: {len(chunk)}文字")
    return True


def test_period_split():
    """句点位置で分割されることを確認"""
    print("\n=== test_period_split ===")
    # 句点を含む長いメッセージ（改行なし）
    sentence1 = "あ" * 1500 + "。"
    sentence2 = "い" * 600
    message = sentence1 + sentence2

    result = split_message(message)

    assert len(result) >= 2, f"Expected at least 2 chunks, got {len(result)}"
    assert all(len(chunk) <= DISCORD_MAX_LENGTH for chunk in result)
    # 最初のチャンクは句点で終わるはず
    assert result[0].endswith("。"), "First chunk should end with period"
    print(f"✓ 句点を含むメッセージが{len(result)}つのチャンクに分割される")
    for i, chunk in enumerate(result, 1):
        print(f"  チャンク{i}: {len(chunk)}文字")
    return True


def test_very_long_message():
    """非常に長いメッセージ（5000文字）の分割を確認"""
    print("\n=== test_very_long_message ===")
    message = "あ" * 5000
    result = split_message(message)

    assert len(result) == 3, f"Expected 3 chunks, got {len(result)}"
    assert all(len(chunk) <= DISCORD_MAX_LENGTH for chunk in result)
    assert (
        "".join(result) == message
    ), "Split chunks should reconstruct original message"
    print(f"✓ 5000文字のメッセージが{len(result)}つのチャンクに分割される")
    for i, chunk in enumerate(result, 1):
        print(f"  チャンク{i}: {len(chunk)}文字")
    return True


def test_custom_max_length():
    """カスタムの最大長で分割されることを確認"""
    print("\n=== test_custom_max_length ===")
    message = "あ" * 150
    result = split_message(message, max_length=100)

    assert len(result) == 2, f"Expected 2 chunks, got {len(result)}"
    assert all(len(chunk) <= 100 for chunk in result)
    print(f"✓ カスタム最大長(100)で150文字のメッセージが{len(result)}つに分割される")
    return True


def main():
    """全てのテストを実行"""
    print("\n" + "=" * 60)
    print("メッセージ分割ユーティリティ テスト")
    print("=" * 60 + "\n")

    tests = [
        ("短いメッセージ", test_short_message),
        ("空のメッセージ", test_empty_message),
        ("ちょうど2000文字", test_exact_limit_message),
        ("2000文字超過", test_long_message_split),
        ("改行での分割", test_newline_split),
        ("句点での分割", test_period_split),
        ("非常に長いメッセージ", test_very_long_message),
        ("カスタム最大長", test_custom_max_length),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except AssertionError as e:
            print(f"❌ テスト失敗: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 合格" if result else "❌ 失敗"
        print(f"{status}: {test_name}")

    print(f"\n合計: {passed}/{total} テストに合格")

    if passed == total:
        print("\n✅ 全てのテストに合格しました！")
        return True
    else:
        print("\n⚠ 一部のテストが失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
