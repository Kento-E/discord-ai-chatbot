#!/usr/bin/env python3
"""
LLM API統合機能のテスト
"""
import os
import sys
from unittest.mock import MagicMock, patch


def test_llm_api_availability():
    """
    LLM APIの利用可能性を確認（環境変数チェック）

    このテストはGEMINI_API_KEYの設定状態を確認し、
    その状態を表示します。APIキーの有無にかかわらず常に成功を返します。
    実際のAPI呼び出しテストは別の関数で実施されます。
    """
    print("=== LLM API利用可能性テスト ===\n")

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("✓ GEMINI_API_KEY が設定されています")
        print("  APIが利用可能です")
    else:
        print("⚠ GEMINI_API_KEY が設定されていません")
        print("  BotにはAPIキーが必要です")
        print("  ※ これはテストの失敗ではなく、環境の状態を示しています")
    # APIキーの有無にかかわらず、テストは成功とする（環境の状態を確認するだけ）
    return True


def test_llm_response_generation():
    """LLM応答生成機能のテスト"""
    print("\n=== LLM応答生成テスト ===\n")

    # テスト用の類似メッセージ
    test_similar_messages = [
        "Pythonでファイルを読み込むには、open()関数を使います。",
        "with文を使うと、ファイルを自動的に閉じることができます。",
        "例: with open('file.txt', 'r') as f: content = f.read()",
    ]

    test_query = "Pythonでファイルを読み込む方法を教えてください"

    try:
        from ai_chatbot import generate_response_with_llm

        response, error_message = generate_response_with_llm(
            test_query, test_similar_messages
        )

        if response:
            print("✓ LLM APIからの応答を取得しました")
            print(f"\n【クエリ】\n{test_query}")
            print(f"\n【応答】\n{response}")
            return True
        else:
            if error_message:
                print(f"⚠ LLM APIからの応答がありません: {error_message}")
            else:
                print("⚠ LLM APIからの応答がありません（APIキー未設定またはエラー）")
            return False

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_key_requirement():
    """APIキー必須チェックのテスト"""
    print("\n=== APIキー必須チェックテスト ===\n")

    # 一時的にAPIキーを削除してテスト
    original_key = os.environ.get("GEMINI_API_KEY")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

    try:
        # データベースが存在しない場合はスキップ
        db_path = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "data",
                "knowledge.db",
            )
        )
        if not os.path.exists(db_path):
            print("⚠ データベースが存在しないため、スキップします")
            return True

        from ai_chatbot import generate_response

        test_query = "テスト"

        try:
            generate_response(test_query)
            print("❌ APIキーがなくても応答が返されました（異常）")
            result = False
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("✓ APIキーがない場合、ValueErrorが発生しました（正常）")
                print(f"  エラーメッセージ: {str(e)}")
                result = True
            else:
                print(f"❌ 予期しないValueError: {e}")
                result = False

    finally:
        # APIキーを復元
        if original_key:
            os.environ["GEMINI_API_KEY"] = original_key

    return result


def test_integration_with_generate_response():
    """generate_response()関数との統合テスト"""
    print("\n=== generate_response()統合テスト ===\n")

    # このテストはデータベースが必要なため、
    # データが存在する場合のみ実行
    db_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data",
            "knowledge.db",
        )
    )

    if not os.path.exists(db_path):
        print("⚠ データベースが存在しないため、スキップします")
        return True

    try:
        from ai_chatbot import generate_response

        test_query = "こんにちは"
        response = generate_response(test_query)

        print("✓ generate_response()が正常に動作しました")
        print(f"\n【クエリ】\n{test_query}")
        print(f"\n【応答】\n{response}")

        # 応答が空でないことを確認
        if response and len(response) > 0:
            print("\n✓ 有効な応答が生成されました")
            return True
        else:
            print("\n❌ 応答が空です")
            return False

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_prompt_structure():
    """プロンプト構造のテスト（APIコールなし）"""
    print("\n=== プロンプト構造テスト ===\n")

    try:
        # テスト用のメッセージ
        test_similar_messages = [
            "過去のメッセージ1",
            "過去のメッセージ2",
        ]
        test_query = "テスト質問"

        # 環境変数を一時的に設定
        original_role = os.environ.get("ADDITIONAL_CHATBOT_ROLE")
        original_api_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "test_key"
        os.environ["ADDITIONAL_CHATBOT_ROLE"] = "あなたはテスト用の役割です。"

        try:
            import ai_chatbot

            # モジュールのキャッシュをクリア
            ai_chatbot._prompts = None
            ai_chatbot._cached_additional_role = None
            ai_chatbot._gemini_model = None
            ai_chatbot._gemini_module = None

            # モックレスポンスとモデルを作成
            mock_response = MagicMock()
            mock_response.text = "テスト応答"

            mock_genai = MagicMock()
            mock_genai.types.GenerationConfig = MagicMock

            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response

            # Geminiモジュールとモデルをモック
            with patch("ai_chatbot._gemini_module", mock_genai):
                with patch("ai_chatbot._gemini_model", mock_model):
                    with patch("ai_chatbot._safety_settings", []):
                        from ai_chatbot import generate_response_with_llm

                        # 関数を呼び出し
                        response, error = generate_response_with_llm(
                            test_query, test_similar_messages
                        )

                        # generate_content が呼ばれたことを確認
                        assert (
                            mock_model.generate_content.called
                        ), "generate_content が呼ばれませんでした"

                        # 呼び出し時の引数（prompt）を取得
                        call_args = mock_model.generate_content.call_args
                        prompt = call_args[0][0]  # 最初の位置引数がプロンプト

                        print("✓ プロンプト構造を検証:")
                        print(f"  プロンプト長: {len(prompt)} 文字\n")

                        # 1. システムプロンプトが先頭にあること
                        assert prompt.startswith(
                            "あなたは"
                        ), "システムプロンプトが先頭にありません"
                        print("  ✓ システムプロンプトが先頭に配置されています")

                        # 2. 追加の役割が含まれていること
                        assert (
                            "【追加の役割・性格】" in prompt
                        ), "追加の役割セクションが見つかりません"
                        assert (
                            "テスト用の役割" in prompt
                        ), "追加の役割の内容が含まれていません"
                        print("  ✓ 追加の役割が統合されています")

                        # 3. 応答指示が含まれていること
                        assert (
                            "上記の過去メッセージに基づいて" in prompt
                        ), "応答指示が見つかりません"
                        print("  ✓ 応答指示が統合されています")

                        # 4. プロンプトの構造順序を確認
                        system_start = prompt.find("あなたは")
                        role_pos = prompt.find("【追加の役割・性格】")
                        instruction_pos = prompt.find("上記の過去メッセージに基づいて")
                        context_pos = prompt.find("【過去メッセージ】")
                        query_pos = prompt.find("【ユーザーの質問】")

                        # 順序検証: システム < 追加役割 < 応答指示 < コンテキスト < クエリ
                        assert (
                            system_start < role_pos
                        ), "システムプロンプトが追加の役割より後にあります"
                        assert (
                            role_pos < instruction_pos
                        ), "追加の役割が応答指示より後にあります"
                        assert (
                            instruction_pos < context_pos
                        ), "応答指示がコンテキストより後にあります"
                        assert (
                            context_pos < query_pos
                        ), "コンテキストがクエリより後にあります"
                        print("  ✓ プロンプト要素の順序が正しい:")
                        print(
                            "    システムプロンプト → 追加の役割 → 応答指示 → コンテキスト → クエリ"
                        )

                        # 5. コンテキストとクエリが含まれていること
                        assert (
                            "過去のメッセージ1" in prompt
                        ), "コンテキストが含まれていません"
                        assert "テスト質問" in prompt, "クエリが含まれていません"
                        print("  ✓ コンテキストとクエリが正しく配置されています")

                        print("\n✅ プロンプト構造のすべての検証に成功しました")
                        return True

        finally:
            # 環境変数を復元
            if original_role is not None:
                os.environ["ADDITIONAL_CHATBOT_ROLE"] = original_role
            elif "ADDITIONAL_CHATBOT_ROLE" in os.environ:
                del os.environ["ADDITIONAL_CHATBOT_ROLE"]

            if original_api_key is not None:
                os.environ["GEMINI_API_KEY"] = original_api_key
            elif "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]

            # モジュールのキャッシュをクリア
            import ai_chatbot

            ai_chatbot._prompts = None
            ai_chatbot._cached_additional_role = None
            ai_chatbot._gemini_model = None
            ai_chatbot._gemini_module = None

    except AssertionError as e:
        print(f"❌ アサーション失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("LLM API統合機能テスト")
    print("=" * 60 + "\n")

    results = []

    # テスト1: API利用可能性
    results.append(("API利用可能性", test_llm_api_availability()))

    # テスト2: プロンプト構造（モック使用、API呼び出しなし）
    results.append(("プロンプト構造", test_prompt_structure()))

    # テスト3: LLM応答生成
    api_available = os.environ.get("GEMINI_API_KEY") is not None
    if api_available:
        results.append(("LLM応答生成", test_llm_response_generation()))
    else:
        print("\n⚠ GEMINI_API_KEYが設定されていないため、")
        print("  LLM応答生成テストをスキップします")

    # テスト4: APIキー必須チェック
    results.append(("APIキー必須チェック", test_api_key_requirement()))

    # テスト5: generate_response()統合
    if api_available:
        results.append(
            ("generate_response()統合", test_integration_with_generate_response())
        )
    else:
        print("\n⚠ GEMINI_API_KEYが設定されていないため、")
        print("  generate_response()統合テストをスキップします")

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
