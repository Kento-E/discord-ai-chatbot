#!/usr/bin/env python3
"""
新しいプロンプトカスタマイズ環境変数のテスト

CUSTOM_SYSTEM_PROMPT, CUSTOM_RESPONSE_INSTRUCTION,
CUSTOM_*_HEADER などの環境変数が正しく動作することを確認します。
"""

import os
import sys
import tempfile

import yaml


def test_custom_system_prompt():
    """CUSTOM_SYSTEM_PROMPTが正しく適用されるかテスト"""
    print("\n[テスト1] CUSTOM_SYSTEM_PROMPTの適用")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "デフォルトのシステムプロンプト",
                "llm_response_instruction": "デフォルトの応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        # 環境変数を設定
        os.environ["CUSTOM_SYSTEM_PROMPT"] = "カスタムシステムプロンプト"

        result = ai_chatbot._load_prompts()

        assert (
            result["llm_system_prompt"] == "カスタムシステムプロンプト"
        ), f"期待値: 'カスタムシステムプロンプト', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ CUSTOM_SYSTEM_PROMPTが正しく適用されました")

        # クリーンアップ
        del os.environ["CUSTOM_SYSTEM_PROMPT"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_custom_response_instruction():
    """CUSTOM_RESPONSE_INSTRUCTIONが正しく適用されるかテスト"""
    print("\n[テスト2] CUSTOM_RESPONSE_INSTRUCTIONの適用")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "システムプロンプト",
                "llm_response_instruction": "デフォルトの応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None

        os.environ["CUSTOM_RESPONSE_INSTRUCTION"] = "カスタム応答指示"

        result = ai_chatbot._load_prompts()

        assert (
            result["llm_response_instruction"] == "カスタム応答指示"
        ), f"期待値: 'カスタム応答指示', 実際: '{result['llm_response_instruction']}'"
        print("  ✅ CUSTOM_RESPONSE_INSTRUCTIONが正しく適用されました")

        del os.environ["CUSTOM_RESPONSE_INSTRUCTION"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_custom_headers():
    """カスタムヘッダー環境変数が正しく適用されるかテスト"""
    print("\n[テスト3] カスタムヘッダーの適用")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "システムプロンプト",
                "llm_context_header": "【過去メッセージ】",
                "llm_query_header": "【ユーザーの質問】",
                "llm_response_header": "【回答】",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None

        os.environ["CUSTOM_CONTEXT_HEADER"] = "【参考情報】"
        os.environ["CUSTOM_QUERY_HEADER"] = "【お問い合わせ】"
        os.environ["CUSTOM_RESPONSE_HEADER"] = "【返答】"

        result = ai_chatbot._load_prompts()

        assert result["llm_context_header"] == "【参考情報】"
        assert result["llm_query_header"] == "【お問い合わせ】"
        assert result["llm_response_header"] == "【返答】"
        print("  ✅ カスタムヘッダーが正しく適用されました")

        del os.environ["CUSTOM_CONTEXT_HEADER"]
        del os.environ["CUSTOM_QUERY_HEADER"]
        del os.environ["CUSTOM_RESPONSE_HEADER"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_additional_role_with_custom_prompt():
    """ADDITIONAL_CHATBOT_ROLEとカスタムプロンプトの併用テスト"""
    print("\n[テスト4] ADDITIONAL_CHATBOT_ROLEとカスタムプロンプトの併用")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {"llm_system_prompt": "基本プロンプト"},
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None

        os.environ["CUSTOM_SYSTEM_PROMPT"] = "カスタムプロンプト"
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "追加の役割"

        result = ai_chatbot._load_prompts()

        # CUSTOM_SYSTEM_PROMPTが優先され、その後ADDITIONAL_CHATBOT_ROLEが追加される
        expected = "カスタムプロンプト\n\n【追加の役割・性格】\n追加の役割"
        assert (
            result["llm_system_prompt"] == expected
        ), f"期待値: '{expected}', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ カスタムプロンプトと追加の役割が正しく併用されました")

        del os.environ["CUSTOM_SYSTEM_PROMPT"]
        del os.environ["ADDITIONAL_CHATBOT_ROLE"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_empty_env_vars_ignored():
    """空の環境変数が無視されることをテスト"""
    print("\n[テスト5] 空の環境変数は無視される")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "デフォルトプロンプト",
                "llm_response_instruction": "デフォルト指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None

        # 空の環境変数を設定
        os.environ["CUSTOM_SYSTEM_PROMPT"] = "   "  # 空白のみ
        os.environ["CUSTOM_RESPONSE_INSTRUCTION"] = ""  # 空文字列

        result = ai_chatbot._load_prompts()

        # 空の環境変数は無視され、デフォルト値が使用される
        assert result["llm_system_prompt"] == "デフォルトプロンプト"
        assert result["llm_response_instruction"] == "デフォルト指示"
        print("  ✅ 空の環境変数が正しく無視されました")

        del os.environ["CUSTOM_SYSTEM_PROMPT"]
        del os.environ["CUSTOM_RESPONSE_INSTRUCTION"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_cache_invalidation_on_env_change():
    """環境変数変更時のキャッシュ無効化テスト"""
    print("\n[テスト6] 環境変数変更時のキャッシュ無効化")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {"llm_system_prompt": "ベースプロンプト"},
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None

        # 初回ロード
        os.environ["CUSTOM_SYSTEM_PROMPT"] = "プロンプト1"
        result1 = ai_chatbot._load_prompts()
        assert result1["llm_system_prompt"] == "プロンプト1"

        # 環境変数を変更
        os.environ["CUSTOM_SYSTEM_PROMPT"] = "プロンプト2"
        result2 = ai_chatbot._load_prompts()

        # キャッシュが無効化され、新しい値が反映される
        assert (
            result2["llm_system_prompt"] == "プロンプト2"
        ), "環境変数変更時にキャッシュが無効化されませんでした"
        print("  ✅ 環境変数変更時にキャッシュが正しく無効化されました")

        del os.environ["CUSTOM_SYSTEM_PROMPT"]
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("新しいプロンプトカスタマイズ環境変数のテスト")
    print("=" * 60)

    tests = [
        test_custom_system_prompt,
        test_custom_response_instruction,
        test_custom_headers,
        test_additional_role_with_custom_prompt,
        test_empty_env_vars_ignored,
        test_cache_invalidation_on_env_change,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ テスト失敗: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ エラー発生: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print("テスト結果")
    print("=" * 60)
    print(f"✅ 成功: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"合計: {passed + failed}")

    if failed == 0:
        print("\n🎉 すべてのテストが成功しました！")
        return True
    else:
        print(f"\n⚠️  {failed}個のテストが失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
