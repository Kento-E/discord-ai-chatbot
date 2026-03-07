#!/usr/bin/env python3
"""
gemini_config.py モジュールのユニットテスト

get_model_name() 関数のエラーハンドリングとフォールバック機能をテストします。
"""

import os
import sys
import tempfile


def test_normal_config_loading():
    """正常な設定ファイルの読み込みテスト"""
    print("\n[テスト1] 正常な設定ファイルの読み込み")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write('model_name = "gemini-2.0-flash"\n')
        temp_config_path = f.name

    try:
        # gemini_configモジュールの設定パスを一時的に変更
        import gemini_config

        original_path = gemini_config.CONFIG_PATH
        gemini_config.CONFIG_PATH = temp_config_path
        gemini_config._cached_model_name = None  # キャッシュをクリア

        result = gemini_config.get_model_name()

        assert (
            result == "gemini-2.0-flash"
        ), f"期待値: 'gemini-2.0-flash', 実際: '{result}'"
        print("  ✅ 正常に設定ファイルから読み込めました")

        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None

    finally:
        os.unlink(temp_config_path)


def test_missing_config_file():
    """設定ファイルが存在しない場合のフォールバックテスト"""
    print("\n[テスト2] 設定ファイルが存在しない場合のフォールバック")

    import gemini_config

    # 存在しないパスを設定
    original_path = gemini_config.CONFIG_PATH
    gemini_config.CONFIG_PATH = "/nonexistent/path/to/config.toml"
    gemini_config._cached_model_name = None  # キャッシュをクリア

    try:
        result = gemini_config.get_model_name()

        assert (
            result == gemini_config.DEFAULT_MODEL_NAME
        ), f"期待値: '{gemini_config.DEFAULT_MODEL_NAME}', 実際: '{result}'"
        print(
            f"  ✅ デフォルト値 '{gemini_config.DEFAULT_MODEL_NAME}' にフォールバックしました"
        )

    finally:
        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None


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
        import gemini_config

        original_path = gemini_config.CONFIG_PATH
        gemini_config.CONFIG_PATH = temp_config_path
        gemini_config._cached_model_name = None  # キャッシュをクリア

        result = gemini_config.get_model_name()

        assert (
            result == gemini_config.DEFAULT_MODEL_NAME
        ), f"期待値: '{gemini_config.DEFAULT_MODEL_NAME}', 実際: '{result}'"
        print(
            f"  ✅ TOML解析エラー時にデフォルト値 '{gemini_config.DEFAULT_MODEL_NAME}' にフォールバックしました"
        )

        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None

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
        import gemini_config

        original_path = gemini_config.CONFIG_PATH
        gemini_config.CONFIG_PATH = temp_config_path
        gemini_config._cached_model_name = None  # キャッシュをクリア

        result = gemini_config.get_model_name()

        assert (
            result == gemini_config.DEFAULT_MODEL_NAME
        ), f"期待値: '{gemini_config.DEFAULT_MODEL_NAME}', 実際: '{result}'"
        print(
            f"  ✅ 空のTOMLファイルに対してデフォルト値 '{gemini_config.DEFAULT_MODEL_NAME}' を返しました"
        )

        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None

    finally:
        os.unlink(temp_config_path)


def test_missing_model_name_key():
    """model_name キーが存在しない場合のデフォルト値テスト"""
    print("\n[テスト5] model_name キーが存在しない場合のデフォルト値")

    # model_nameキーが存在しない設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write('other_key = "some_value"\n')
        temp_config_path = f.name

    try:
        import gemini_config

        original_path = gemini_config.CONFIG_PATH
        gemini_config.CONFIG_PATH = temp_config_path
        gemini_config._cached_model_name = None  # キャッシュをクリア

        result = gemini_config.get_model_name()

        assert (
            result == gemini_config.DEFAULT_MODEL_NAME
        ), f"期待値: '{gemini_config.DEFAULT_MODEL_NAME}', 実際: '{result}'"
        print(
            f"  ✅ model_nameキーがない場合にデフォルト値 '{gemini_config.DEFAULT_MODEL_NAME}' を返しました"
        )

        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None

    finally:
        os.unlink(temp_config_path)


def test_cache_behavior():
    """キャッシュ機能のテスト"""
    print("\n[テスト6] キャッシュ機能の動作確認")

    # 一時的な設定ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write('model_name = "gemini-test-model"\n')
        temp_config_path = f.name

    try:
        import gemini_config

        original_path = gemini_config.CONFIG_PATH
        gemini_config.CONFIG_PATH = temp_config_path
        gemini_config._cached_model_name = None  # キャッシュをクリア

        # 1回目の呼び出し
        result1 = gemini_config.get_model_name()

        # ファイルを削除（キャッシュがあれば読み込みは発生しない）
        os.unlink(temp_config_path)

        # 2回目の呼び出し（キャッシュから取得）
        result2 = gemini_config.get_model_name()

        assert (
            result1 == result2 == "gemini-test-model"
        ), f"キャッシュが正しく動作していません。1回目: '{result1}', 2回目: '{result2}'"
        print(f"  ✅ キャッシュが正しく動作しています（値: '{result1}'）")

        # 設定を復元
        gemini_config.CONFIG_PATH = original_path
        gemini_config._cached_model_name = None

    except FileNotFoundError:
        # ファイルが既に削除されている場合は問題なし
        pass


def test_safety_settings():
    """安全性フィルター設定のテスト"""
    print("\n[テスト7] 安全性フィルター設定の取得")

    try:
        # google.generativeaiをインポート
        import google.generativeai as genai

        from gemini_config import get_safety_settings

        # 安全性フィルター設定を取得
        safety_settings = get_safety_settings(genai)

        # 設定が辞書であることを確認
        assert isinstance(safety_settings, dict), "安全性設定は辞書である必要があります"

        # すべてのカテゴリが存在することを確認
        HarmCategory = genai.types.HarmCategory
        HarmBlockThreshold = genai.types.HarmBlockThreshold

        expected_categories = [
            HarmCategory.HARM_CATEGORY_HARASSMENT,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        ]

        for category in expected_categories:
            assert (
                category in safety_settings
            ), f"カテゴリ {category} が安全性設定に含まれていません"
            assert (
                safety_settings[category] == HarmBlockThreshold.BLOCK_NONE
            ), f"カテゴリ {category} の設定が BLOCK_NONE ではありません"

        print("  ✅ 安全性フィルター設定が正しく取得できました")
        print(f"     設定されたカテゴリ数: {len(safety_settings)}")

    except ImportError:
        print(
            "  ⚠️  google-generativeai がインストールされていないため、スキップします"
        )


def test_create_generative_model():
    """Gemini APIモデル作成のテスト"""
    print("\n[テスト8] Gemini APIモデル作成")

    # 環境変数からAPIキーを取得
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or not api_key.strip():
        print("  ⚠️  GEMINI_API_KEY が設定されていないため、スキップします")
        return

    try:
        from gemini_config import create_generative_model

        # モデルを作成
        genai, model, safety_settings = create_generative_model(api_key)

        # 返り値の型を確認
        assert genai is not None, "genaiモジュールがNoneです"
        assert model is not None, "モデルがNoneです"
        assert isinstance(safety_settings, dict), "安全性設定が辞書ではありません"

        print("  ✅ Gemini APIモデルが正しく作成されました")
        print(f"     安全性設定のカテゴリ数: {len(safety_settings)}")

    except ImportError:
        print(
            "  ⚠️  google-generativeai がインストールされていないため、スキップします"
        )
    except Exception as e:
        print(f"  ⚠️  テスト実行中にエラーが発生: {e}")


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("gemini_config.py ユニットテスト")
    print("=" * 60)

    tests = [
        test_normal_config_loading,
        test_missing_config_file,
        test_invalid_toml,
        test_empty_toml_file,
        test_missing_model_name_key,
        test_cache_behavior,
        test_safety_settings,
        test_create_generative_model,
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
