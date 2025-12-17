#!/usr/bin/env python3
"""
知識データ優先機能のテスト

このテストは、修正後のプロンプト設定が正しく読み込まれ、
知識データを優先するための指示が含まれていることを確認します。
"""
import os
import sys


def test_prompt_contains_priority_instructions():
    """
    プロンプト設定に知識データ優先の指示が含まれているか確認
    """
    print("=== 知識データ優先プロンプトテスト ===\n")

    try:
        # プロンプト設定を読み込み
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ai_agent import _load_prompts

        prompts = _load_prompts()

        # システムプロンプトの確認
        system_prompt = prompts.get("llm_system_prompt", "")
        print("【システムプロンプトの内容確認】")

        # 重要なキーワードをチェック
        keywords_to_check = [
            ("専門AIアシスタント", "AIの役割が専門的なアシスタントとして定義されている"),
            ("最優先", "知識データの優先が明示されている"),
            ("知識データ", "知識データという用語が使用されている"),
            ("過去メッセージ", "過去メッセージへの言及がある"),
        ]

        passed_checks = 0
        total_checks = len(keywords_to_check)

        for keyword, description in keywords_to_check:
            if keyword in system_prompt:
                print(f"  ✅ {description}")
                passed_checks += 1
            else:
                print(f"  ❌ {description} - キーワード '{keyword}' が見つかりません")

        # 回答指示の確認
        response_instruction = prompts.get("llm_response_instruction", "")
        print("\n【回答生成指示の内容確認】")

        instruction_keywords = [
            ("過去メッセージの内容を最優先", "過去メッセージ優先の指示がある"),
            ("一般的な知識", "一般知識の扱いについて言及がある"),
            ("補足", "一般知識は補足的な使用に限定されている"),
        ]

        for keyword, description in instruction_keywords:
            if keyword in response_instruction:
                print(f"  ✅ {description}")
                passed_checks += 1
            else:
                print(f"  ❌ {description} - キーワード '{keyword}' が見つかりません")

        total_checks += len(instruction_keywords)

        # 結果サマリー
        print(f"\n【結果】")
        print(f"チェック項目: {passed_checks}/{total_checks} 合格")

        if passed_checks == total_checks:
            print("✅ すべてのチェックに合格しました")
            print("   知識データ優先の設定が正しく適用されています")
            return True
        else:
            print("⚠️ 一部のチェックが失敗しました")
            print("   プロンプト設定を確認してください")
            return False

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_prompt_structure():
    """
    プロンプト設定の構造が正しいか確認
    """
    print("\n=== プロンプト構造テスト ===\n")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ai_agent import _load_prompts

        prompts = _load_prompts()

        required_keys = [
            "llm_system_prompt",
            "llm_response_instruction",
            "llm_context_header",
            "llm_query_header",
            "llm_response_header",
        ]

        print("【必須キーの存在確認】")
        all_present = True
        for key in required_keys:
            if key in prompts:
                print(f"  ✅ {key} - 存在")
            else:
                print(f"  ❌ {key} - 存在しない")
                all_present = False

        if all_present:
            print("\n✅ すべての必須キーが存在します")
            return True
        else:
            print("\n❌ 一部の必須キーが不足しています")
            return False

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("知識データ優先機能テスト")
    print("=" * 60 + "\n")

    results = []

    # テスト1: プロンプトに優先指示が含まれているか
    results.append(("知識データ優先指示の確認", test_prompt_contains_priority_instructions()))

    # テスト2: プロンプト構造の確認
    results.append(("プロンプト構造の確認", test_prompt_structure()))

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
        print("   知識データ優先の修正が正しく適用されています")
        return True
    else:
        print("\n⚠ 一部のテストが失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
