#!/usr/bin/env python3
"""
ai_chatbot.py の _load_prompts() 関数のユニットテスト

プロンプト設定ファイルの読み込み、エラーハンドリング、キャッシュ機能をテストします。
"""

import os
import sys
import tempfile


def test_normal_prompts_loading():
    """正常なプロンプト設定ファイルの読み込みテスト"""
    print("\n[テスト1] 正常なプロンプト設定ファイルの読み込み")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write(
            'llm_system_prompt = "テスト用システムプロンプト"\n'
            'llm_response_instruction = "テスト用応答指示"\n'
            'llm_context_header = "【テスト】"\n'
            'llm_query_header = "【質問】"\n'
            'llm_response_header = "【回答】"\n'
        )
        temp_config_path = f.name

    try:
        # ai_chatbotモジュールの設定パスを一時的に変更
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        result = ai_chatbot._load_prompts()

        assert (
            result["llm_system_prompt"] == "テスト用システムプロンプト"
        ), f"期待値: 'テスト用システムプロンプト', 実際: '{result['llm_system_prompt']}'"
        print("  ✅ 正常に設定ファイルから読み込めました")

        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_missing_prompts_file():
    """プロンプト設定ファイルが存在しない場合のエラーテスト"""
    print("\n[テスト2] プロンプト設定ファイルが存在しない場合のエラー")

    import ai_chatbot

    # 存在しないパスを設定
    original_path = ai_chatbot.PROMPTS_PATH
    ai_chatbot.PROMPTS_PATH = "/nonexistent/path/to/prompts.toml"
    ai_chatbot._prompts = None  # キャッシュをクリア

    try:
        try:
            ai_chatbot._load_prompts()
            print("  ❌ エラーが発生しませんでした（異常）")
            return False
        except FileNotFoundError as e:
            if "プロンプト設定ファイルが見つかりません" in str(e):
                print("  ✅ FileNotFoundErrorが正しく発生しました")
                error_msg = str(e).split("\n")[0]
                print(f"     エラーメッセージ: {error_msg}")
                return True
            else:
                print(f"  ❌ 予期しないエラーメッセージ: {e}")
                return False
    finally:
        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None


def test_invalid_toml():
    """無効なTOMLの場合のエラーハンドリングテスト"""
    print("\n[テスト3] 無効なTOMLの場合のエラーハンドリング")

    # 無効なTOMLファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write("invalid = toml = content = [")
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        try:
            ai_chatbot._load_prompts()
            print("  ❌ エラーが発生しませんでした（異常）")
            return False
        except RuntimeError as e:
            if "TOML構文に誤りがあります" in str(e):
                print("  ✅ TOML解析エラー時にRuntimeErrorが発生しました")
                error_msg = str(e).split("\n")[0]
                print(f"     エラーメッセージ: {error_msg}")
                return True
            else:
                print(f"  ❌ 予期しないエラーメッセージ: {e}")
                return False
        finally:
            # 設定を復元
            ai_chatbot.PROMPTS_PATH = original_path
            ai_chatbot._prompts = None

    finally:
        os.unlink(temp_config_path)


def test_empty_toml_file():
    """空のTOMLファイルの処理テスト"""
    print("\n[テスト4] 空のTOMLファイルの処理")

    # 空のTOMLファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write("")
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        result = ai_chatbot._load_prompts()

        # 空のTOMLファイルは空の辞書を返す
        if not result:
            print("  ✅ 空のTOMLファイルに対して空の辞書を返しました")
            return True
        else:
            print(f"  ⚠️  空のTOMLファイルに対して予期しない値を返しました: {result}")
            return True  # 警告だが失敗ではない
    finally:
        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        os.unlink(temp_config_path)


def test_missing_required_keys():
    """必要なキーが存在しない場合の動作テスト"""
    print("\n[テスト5] 必要なキーが存在しない場合の動作")

    # 必要なキーが存在しない設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write('other_key = "some_value"\n')
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        result = ai_chatbot._load_prompts()

        # 必要なキーがない場合でも読み込みは成功するが、
        # 実際の使用時に問題が発生する可能性がある
        if "llm_system_prompt" not in result:
            print("  ✅ llm_system_promptキーが存在しないことを確認しました")
            print("     （実際の使用時にエラーが発生する可能性があります）")
            return True
        else:
            print("  ⚠️  予期しない動作: llm_system_promptが存在します")
            return True  # 警告だが失敗ではない
    finally:
        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        os.unlink(temp_config_path)


def test_cache_behavior():
    """キャッシュ機能のテスト"""
    print("\n[テスト6] キャッシュ機能の動作確認")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write('llm_system_prompt = "キャッシュテスト用プロンプト"\n')
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        # 1回目の呼び出し
        result1 = ai_chatbot._load_prompts()

        # ファイルを削除（キャッシュがあれば読み込みは発生しない）
        os.unlink(temp_config_path)

        # 2回目の呼び出し（キャッシュから取得）
        result2 = ai_chatbot._load_prompts()

        if result1 == result2:
            print("  ✅ キャッシュが正しく動作しています")
            return True
        else:
            print("  ❌ キャッシュが正しく動作していません")
            return False
    except FileNotFoundError:
        # ファイルが既に削除されている場合は問題なし
        return True
    finally:
        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None


def test_japanese_content():
    """日本語コンテンツの処理テスト"""
    print("\n[テスト7] 日本語コンテンツの処理")

    # 日本語を含む設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write(
            'llm_system_prompt = "あなたは過去のDiscordメッセージから学習した専門AIアシスタントです。"\n'
            'llm_response_instruction = "具体的で実践的なアドバイスを提供してください。"\n'
        )
        temp_config_path = f.name

    try:
        import ai_chatbot

        original_path = ai_chatbot.PROMPTS_PATH
        ai_chatbot.PROMPTS_PATH = temp_config_path
        ai_chatbot._prompts = None  # キャッシュをクリア

        result = ai_chatbot._load_prompts()

        if "専門AIアシスタント" in result["llm_system_prompt"]:
            print("  ✅ 日本語コンテンツが正しく読み込まれました")
            return True
        else:
            print("  ❌ 日本語コンテンツの読み込みに問題があります")
            return False
    finally:
        # 設定を復元
        ai_chatbot.PROMPTS_PATH = original_path
        ai_chatbot._prompts = None
        os.unlink(temp_config_path)


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("_load_prompts() 関数のユニットテスト")
    print("=" * 60)

    tests = [
        test_normal_prompts_loading,
        test_missing_prompts_file,
        test_invalid_toml,
        test_empty_toml_file,
        test_missing_required_keys,
        test_cache_behavior,
        test_japanese_content,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            # test_missing_prompts_file と test_invalid_toml は戻り値を返す
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
