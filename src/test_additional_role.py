#!/usr/bin/env python3
"""
追加の役割指定機能のテスト

ADDITIONAL_AGENT_ROLE 環境変数が正しくシステムプロンプトに統合されることを確認します。
"""

import os
import sys
import tempfile

import yaml


def test_no_additional_role():
    """追加の役割が設定されていない場合の動作テスト"""
    print("\n[テスト1] 追加の役割が設定されていない場合")

    # 環境変数をクリア
    if "ADDITIONAL_AGENT_ROLE" in os.environ:
        del os.environ["ADDITIONAL_AGENT_ROLE"]

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
                "llm_response_instruction": "応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        result = ai_agent._load_prompts()

        assert (
            result["llm_system_prompt"] == "ベースのシステムプロンプト"
        ), f"期待値: 'ベースのシステムプロンプト', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ 追加の役割がない場合、ベースのプロンプトのみが使用されます")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)


def test_with_additional_role():
    """追加の役割が設定されている場合の動作テスト"""
    print("\n[テスト2] 追加の役割が設定されている場合")

    # 環境変数を設定
    os.environ["ADDITIONAL_AGENT_ROLE"] = "あなたは親切で丁寧なサポート担当者です。"

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
                "llm_response_instruction": "応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        result = ai_agent._load_prompts()

        expected = (
            "ベースのシステムプロンプト\n\n"
            "【追加の役割・性格】\n"
            "あなたは親切で丁寧なサポート担当者です。"
        )
        assert (
            result["llm_system_prompt"] == expected
        ), f"期待値: '{expected}', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ 追加の役割が正しくシステムプロンプトに統合されました")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)
        if "ADDITIONAL_AGENT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_AGENT_ROLE"]


def test_with_empty_additional_role():
    """追加の役割が空文字列の場合の動作テスト"""
    print("\n[テスト3] 追加の役割が空文字列の場合")

    # 環境変数を空文字列に設定
    os.environ["ADDITIONAL_AGENT_ROLE"] = ""

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
                "llm_response_instruction": "応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        result = ai_agent._load_prompts()

        assert (
            result["llm_system_prompt"] == "ベースのシステムプロンプト"
        ), f"期待値: 'ベースのシステムプロンプト', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ 空文字列の場合、ベースのプロンプトのみが使用されます")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)
        if "ADDITIONAL_AGENT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_AGENT_ROLE"]


def test_with_whitespace_only_role():
    """追加の役割が空白文字のみの場合の動作テスト"""
    print("\n[テスト4] 追加の役割が空白文字のみの場合")

    # 環境変数を空白文字に設定
    os.environ["ADDITIONAL_AGENT_ROLE"] = "   \n\t  "

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
                "llm_response_instruction": "応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        result = ai_agent._load_prompts()

        assert (
            result["llm_system_prompt"] == "ベースのシステムプロンプト"
        ), f"期待値: 'ベースのシステムプロンプト', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ 空白文字のみの場合、ベースのプロンプトのみが使用されます")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)
        if "ADDITIONAL_AGENT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_AGENT_ROLE"]


def test_multiline_additional_role():
    """複数行の追加の役割の動作テスト"""
    print("\n[テスト5] 複数行の追加の役割")

    # 環境変数を複数行のテキストに設定
    multiline_role = """あなたは経験豊富なエンジニアです。
以下の特徴があります：
- 技術的な問題を分かりやすく説明できる
- ベストプラクティスを理解している
- セキュリティを重視する"""
    os.environ["ADDITIONAL_AGENT_ROLE"] = multiline_role

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
                "llm_response_instruction": "応答指示",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        result = ai_agent._load_prompts()

        assert (
            "ベースのシステムプロンプト" in result["llm_system_prompt"]
        ), "ベースのプロンプトが含まれていません"
        assert (
            "【追加の役割・性格】" in result["llm_system_prompt"]
        ), "追加の役割セクションが含まれていません"
        assert (
            "あなたは経験豊富なエンジニアです。" in result["llm_system_prompt"]
        ), "追加の役割の内容が含まれていません"
        print("  ✅ 複数行の追加の役割が正しく統合されました")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)
        if "ADDITIONAL_AGENT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_AGENT_ROLE"]


def test_cache_with_additional_role():
    """追加の役割適用後のキャッシュ動作テスト"""
    print("\n[テスト6] 追加の役割適用後のキャッシュ動作")

    # 環境変数を設定
    os.environ["ADDITIONAL_AGENT_ROLE"] = "テスト用の追加役割"

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "ベースのシステムプロンプト",
            },
            f,
            allow_unicode=True,
        )
        temp_config_path = f.name

    try:
        import ai_agent

        original_path = ai_agent.PROMPTS_PATH
        ai_agent.PROMPTS_PATH = temp_config_path
        ai_agent._prompts = None  # キャッシュをクリア

        # 1回目の呼び出し
        result1 = ai_agent._load_prompts()

        # 2回目の呼び出し（キャッシュから取得）
        result2 = ai_agent._load_prompts()

        assert result1 == result2, "キャッシュが正しく動作していません"
        assert (
            "【追加の役割・性格】" in result1["llm_system_prompt"]
        ), "追加の役割が適用されていません"
        print("  ✅ 追加の役割適用後もキャッシュが正しく動作しています")

        # 設定を復元
        ai_agent.PROMPTS_PATH = original_path
        ai_agent._prompts = None

        return True
    finally:
        os.unlink(temp_config_path)
        if "ADDITIONAL_AGENT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_AGENT_ROLE"]


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("追加の役割指定機能のテスト")
    print("=" * 60)

    tests = [
        test_no_additional_role,
        test_with_additional_role,
        test_with_empty_additional_role,
        test_with_whitespace_only_role,
        test_multiline_additional_role,
        test_cache_with_additional_role,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
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
