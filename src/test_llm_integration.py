#!/usr/bin/env python3
"""
LLM API統合機能のテスト
"""
import os
import sys


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
        from ai_agent import generate_response_with_llm

        response = generate_response_with_llm(test_query, test_similar_messages)

        if response:
            print("✓ LLM APIからの応答を取得しました")
            print(f"\n【クエリ】\n{test_query}")
            print(f"\n【応答】\n{response}")
            return True
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
        # 埋め込みデータが存在しない場合はスキップ
        embed_path = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "data",
                "embeddings.json",
            )
        )
        if not os.path.exists(embed_path):
            print("⚠ 埋め込みデータが存在しないため、スキップします")
            return True

        from ai_agent import generate_response

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

    # このテストは埋め込みデータが必要なため、
    # データが存在する場合のみ実行
    embed_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data",
            "embeddings.json",
        )
    )

    if not os.path.exists(embed_path):
        print("⚠ 埋め込みデータが存在しないため、スキップします")
        return True

    try:
        from ai_agent import generate_response

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


def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("LLM API統合機能テスト")
    print("=" * 60 + "\n")

    results = []

    # テスト1: API利用可能性
    results.append(("API利用可能性", test_llm_api_availability()))

    # テスト2: LLM応答生成
    api_available = os.environ.get("GEMINI_API_KEY") is not None
    if api_available:
        results.append(("LLM応答生成", test_llm_response_generation()))
    else:
        print("\n⚠ GEMINI_API_KEYが設定されていないため、")
        print("  LLM応答生成テストをスキップします")

    # テスト3: APIキー必須チェック
    results.append(("APIキー必須チェック", test_api_key_requirement()))

    # テスト4: generate_response()統合
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
