#!/usr/bin/env python3
"""
is_llm_mode_enabled()関数のテスト

このテストでは、main.pyのis_llm_mode_enabled()関数の動作を検証します。
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Discordモジュールのモック
sys.modules["discord"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()


def test_is_llm_mode_enabled():
    """is_llm_mode_enabled()関数の包括的テスト"""
    print("=== is_llm_mode_enabled()関数のテスト ===\n")

    # main.pyから関数をインポート
    # 環境変数を事前にモック
    test_env = {
        "DISCORD_TOKEN": "test_token",
        "TARGET_GUILD_ID": "123456789",
    }

    # テストケース1: GEMINI_API_KEYが設定されている場合
    print("テスト1: GEMINI_API_KEYが設定されている場合")
    with patch.dict(
        os.environ, {**test_env, "GEMINI_API_KEY": "test_api_key_123"}, clear=True
    ):
        # モジュールを動的にインポート
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "main_module",
            "/home/runner/work/discord-ai-agent/discord-ai-agent/src/main.py",
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)

        result = main_module.is_llm_mode_enabled()
        assert result is True, "✗ GEMINI_API_KEYが設定されている場合、Trueを返すべき"
        print("  ✓ 結果: True（正常）\n")

    # テストケース2: GEMINI_API_KEYが未設定の場合
    print("テスト2: GEMINI_API_KEYが未設定の場合")
    with patch.dict(os.environ, test_env, clear=True):
        spec = importlib.util.spec_from_file_location(
            "main_module2",
            "/home/runner/work/discord-ai-agent/discord-ai-agent/src/main.py",
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)

        result = main_module.is_llm_mode_enabled()
        assert result is False, "✗ GEMINI_API_KEYが未設定の場合、Falseを返すべき"
        print("  ✓ 結果: False（正常）\n")

    # テストケース3: GEMINI_API_KEYが空文字列の場合
    print("テスト3: GEMINI_API_KEYが空文字列の場合")
    with patch.dict(os.environ, {**test_env, "GEMINI_API_KEY": ""}, clear=True):
        spec = importlib.util.spec_from_file_location(
            "main_module3",
            "/home/runner/work/discord-ai-agent/discord-ai-agent/src/main.py",
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)

        result = main_module.is_llm_mode_enabled()
        assert result is False, "✗ GEMINI_API_KEYが空文字列の場合、Falseを返すべき"
        print("  ✓ 結果: False（正常）\n")

    # テストケース4: GEMINI_API_KEYが空白のみの場合
    print("テスト4: GEMINI_API_KEYが空白のみの場合")
    with patch.dict(os.environ, {**test_env, "GEMINI_API_KEY": "   "}, clear=True):
        spec = importlib.util.spec_from_file_location(
            "main_module4",
            "/home/runner/work/discord-ai-agent/discord-ai-agent/src/main.py",
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)

        result = main_module.is_llm_mode_enabled()
        assert result is False, "✗ GEMINI_API_KEYが空白のみの場合、Falseを返すべき"
        print("  ✓ 結果: False（正常）\n")

    print("✅ すべてのテストが成功しました")
    return True


if __name__ == "__main__":
    print("🧪 is_llm_mode_enabled()関数のテストを開始します\n")
    print("=" * 60)
    print()

    try:
        success = test_is_llm_mode_enabled()
        if success:
            print("\n" + "=" * 60)
            print("\n✅ テスト完了: すべてのケースが正常に動作しています")
            sys.exit(0)
        else:
            print("\n❌ テスト失敗")
            sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
