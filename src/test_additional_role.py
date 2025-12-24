#!/usr/bin/env python3
"""
ADDITIONAL_CHATBOT_ROLE機能のテスト

追加の役割がシステムプロンプトに正しく統合され、
プロンプト構造が適切に構築されることを検証します。
"""

import os
import sys
import tempfile

import yaml


def test_additional_role_integration():
    """追加の役割がシステムプロンプトに統合されることを確認"""
    print("\n[テスト1] 追加の役割の統合")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "あなたは専門AIアシスタントです。",
                "llm_response_instruction": "具体的に回答してください。",
                "llm_context_header": "【過去メッセージ】",
                "llm_query_header": "【質問】",
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
        ai_chatbot._cached_additional_role = None

        # 追加の役割を設定
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = (
            "あなたは経験豊富なシニアエンジニアです。"
        )

        result = ai_chatbot._load_prompts()

        # 追加の役割が統合されていることを確認
        assert "【追加の役割・性格】" in result["llm_system_prompt"], (
            "追加の役割セクションが見つかりません"
        )
        assert "経験豊富なシニアエンジニア" in result["llm_system_prompt"], (
            "追加の役割の内容が統合されていません"
        )
        assert result["llm_system_prompt"].startswith("あなたは専門AIアシスタントです。"), (
            "ベースプロンプトが変更されています"
        )

        print("  ✅ 追加の役割が正しく統合されました")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        ai_chatbot._cached_additional_role = None
        del os.environ["ADDITIONAL_CHATBOT_ROLE"]

    finally:
        os.unlink(temp_config_path)


def test_prompt_structure():
    """プロンプト構造が正しく構築されることを確認"""
    print("\n[テスト2] プロンプト構造の確認")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "あなたは専門AIアシスタントです。",
                "llm_response_instruction": "以下のルールに従って回答してください：\n1. 簡潔に回答する",
                "llm_context_header": "【過去メッセージ】",
                "llm_query_header": "【質問】",
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
        ai_chatbot._cached_additional_role = None

        # 追加の役割を設定
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "あなたはテクニカルサポート担当者です。"

        prompts = ai_chatbot._load_prompts()

        # プロンプト構築をシミュレート
        similar_messages = ["過去のメッセージ1", "過去のメッセージ2"]
        query = "テスト質問"
        context = "\n".join([f"- {msg}" for msg in similar_messages[:5]])

        # 新しい構造（システム指示を統合）
        system_instructions = f"""{prompts['llm_system_prompt']}

{prompts['llm_response_instruction']}"""

        prompt = f"""{system_instructions}

{prompts['llm_context_header']}
{context}

{prompts['llm_query_header']}
{query}

{prompts['llm_response_header']}"""

        # 構造を検証
        lines = prompt.split("\n")

        # システム指示セクションの検証
        assert "あなたは専門AIアシスタントです。" in system_instructions, (
            "ベースプロンプトが見つかりません"
        )
        assert "【追加の役割・性格】" in system_instructions, (
            "追加の役割セクションが見つかりません"
        )
        assert "テクニカルサポート担当者" in system_instructions, (
            "追加の役割が統合されていません"
        )
        assert "以下のルールに従って回答してください" in system_instructions, (
            "応答指示が統合されていません"
        )

        # プロンプト全体の構造検証
        assert "【過去メッセージ】" in prompt, "コンテキストヘッダーが見つかりません"
        assert "過去のメッセージ1" in prompt, "コンテキストが含まれていません"
        assert "【質問】" in prompt, "質問ヘッダーが見つかりません"
        assert "テスト質問" in prompt, "質問が含まれていません"
        assert "【回答】" in prompt, "回答ヘッダーが見つかりません"

        # システム指示がコンテキストより前にあることを確認
        system_index = prompt.index("あなたは専門AIアシスタントです。")
        context_index = prompt.index("【過去メッセージ】")
        assert system_index < context_index, (
            "システム指示がコンテキストより後にあります"
        )

        # 追加の役割が応答指示より前にあることを確認
        role_index = prompt.index("テクニカルサポート担当者")
        instruction_index = prompt.index("以下のルールに従って回答してください")
        assert role_index < instruction_index, (
            "追加の役割が応答指示より後にあります"
        )

        print("  ✅ プロンプト構造が正しく構築されています")
        print(f"     - システム指示セクション（役割+指示）が先頭に配置")
        print(f"     - 追加の役割が応答指示より前に配置")
        print(f"     - コンテキストがシステム指示の後に配置")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        ai_chatbot._cached_additional_role = None
        del os.environ["ADDITIONAL_CHATBOT_ROLE"]

    finally:
        os.unlink(temp_config_path)


def test_without_additional_role():
    """追加の役割がない場合の動作確認"""
    print("\n[テスト3] 追加の役割なしの動作")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "あなたは専門AIアシスタントです。",
                "llm_response_instruction": "具体的に回答してください。",
                "llm_context_header": "【過去メッセージ】",
                "llm_query_header": "【質問】",
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
        ai_chatbot._cached_additional_role = None

        # 追加の役割を設定しない
        if "ADDITIONAL_CHATBOT_ROLE" in os.environ:
            del os.environ["ADDITIONAL_CHATBOT_ROLE"]

        result = ai_chatbot._load_prompts()

        # 追加の役割セクションが含まれていないことを確認
        assert "【追加の役割・性格】" not in result["llm_system_prompt"], (
            "追加の役割が設定されていないのに統合されています"
        )
        assert result["llm_system_prompt"].strip() == "あなたは専門AIアシスタントです。", (
            "ベースプロンプトが変更されています"
        )

        print("  ✅ 追加の役割なしでも正常に動作します")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        ai_chatbot._cached_additional_role = None

    finally:
        os.unlink(temp_config_path)


def test_empty_additional_role():
    """空の追加の役割の処理確認"""
    print("\n[テスト4] 空の追加の役割の処理")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "あなたは専門AIアシスタントです。",
                "llm_response_instruction": "具体的に回答してください。",
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
        ai_chatbot._cached_additional_role = None

        # 空の追加の役割を設定
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "   "

        result = ai_chatbot._load_prompts()

        # 空白のみの場合は統合されないことを確認
        assert "【追加の役割・性格】" not in result["llm_system_prompt"], (
            "空白のみの追加の役割が統合されています"
        )

        print("  ✅ 空白のみの追加の役割は無視されます")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        ai_chatbot._cached_additional_role = None
        del os.environ["ADDITIONAL_CHATBOT_ROLE"]

    finally:
        os.unlink(temp_config_path)


def test_cache_invalidation():
    """環境変数変更時のキャッシュ無効化確認"""
    print("\n[テスト5] キャッシュ無効化の動作")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(
            {
                "llm_system_prompt": "あなたは専門AIアシスタントです。",
                "llm_response_instruction": "具体的に回答してください。",
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
        ai_chatbot._cached_additional_role = None

        # 最初の追加の役割を設定
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "役割A"
        result1 = ai_chatbot._load_prompts()
        assert "役割A" in result1["llm_system_prompt"], "役割Aが統合されていません"

        # 追加の役割を変更
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "役割B"
        result2 = ai_chatbot._load_prompts()
        assert "役割B" in result2["llm_system_prompt"], "役割Bが統合されていません"
        assert "役割A" not in result2["llm_system_prompt"], "古い役割Aが残っています"

        print("  ✅ 環境変数変更時にキャッシュが正しく無効化されます")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        ai_chatbot._cached_additional_role = None
        del os.environ["ADDITIONAL_CHATBOT_ROLE"]

    finally:
        os.unlink(temp_config_path)


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("ADDITIONAL_CHATBOT_ROLE機能のテスト")
    print("=" * 60)

    tests = [
        test_additional_role_integration,
        test_prompt_structure,
        test_without_additional_role,
        test_empty_additional_role,
        test_cache_invalidation,
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
