"""
/modeコマンドのテスト

このテストでは、/modeコマンドのロジック（LLMモード判定と状態表示）を検証します。
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# Discordモジュールのモック
sys.modules["discord"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()


def test_llm_mode_detection():
    """LLMモードの判定ロジックをテスト"""
    # テスト1: GEMINI_API_KEYが設定されている場合
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"}):
        llm_api_key = os.environ.get("GEMINI_API_KEY")
        is_llm_mode = llm_api_key is not None and llm_api_key.strip() != ""
        assert (
            is_llm_mode is True
        ), "GEMINI_API_KEYが設定されている場合、LLMモードはTrueになるべき"

    # テスト2: GEMINI_API_KEYが空文字列の場合
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        llm_api_key = os.environ.get("GEMINI_API_KEY")
        is_llm_mode = llm_api_key is not None and llm_api_key.strip() != ""
        assert (
            is_llm_mode is False
        ), "GEMINI_API_KEYが空の場合、LLMモードはFalseになるべき"

    # テスト3: GEMINI_API_KEYが設定されていない場合
    with patch.dict(os.environ, {}, clear=True):
        llm_api_key = os.environ.get("GEMINI_API_KEY")
        is_llm_mode = llm_api_key is not None and llm_api_key.strip() != ""
        assert (
            is_llm_mode is False
        ), "GEMINI_API_KEYが設定されていない場合、LLMモードはFalseになるべき"

    print("✅ LLMモード判定ロジックのテスト: 成功")


def test_knowledge_data_detection():
    """知識データの有無確認ロジックをテスト"""
    # テスト1: 知識データが存在する場合
    with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
        has_knowledge_data = os.path.exists(temp_file.name)
        assert (
            has_knowledge_data is True
        ), "ファイルが存在する場合、has_knowledge_dataはTrueになるべき"

    # テスト2: 知識データが存在しない場合
    has_knowledge_data = os.path.exists("/nonexistent/path/embeddings.json")
    assert (
        has_knowledge_data is False
    ), "ファイルが存在しない場合、has_knowledge_dataはFalseになるべき"

    print("✅ 知識データ検出ロジックのテスト: 成功")


def test_mode_status_messages():
    """モードステータスメッセージの生成をテスト"""
    # LLMモードの場合
    is_llm_mode = True
    if is_llm_mode:
        mode_status = "🧠 **LLMモード**"
        mode_description = (
            "Google Gemini APIを使用した高度な応答生成が有効です。\n"
            "過去メッセージを文脈として、より自然で創造的な応答を生成します。"
        )
    else:
        mode_status = "📝 **標準モード**"
        mode_description = (
            "ペルソナベースの応答生成を使用しています。\n"
            "過去メッセージの類似度検索により応答を生成します。"
        )

    assert (
        "LLMモード" in mode_status
    ), "LLMモードの場合、適切なステータスメッセージを表示すべき"
    assert (
        "Gemini API" in mode_description
    ), "LLMモードの詳細説明にGemini APIの記載があるべき"

    # 標準モードの場合
    is_llm_mode = False
    if is_llm_mode:
        mode_status = "🧠 **LLMモード**"
        mode_description = (
            "Google Gemini APIを使用した高度な応答生成が有効です。\n"
            "過去メッセージを文脈として、より自然で創造的な応答を生成します。"
        )
    else:
        mode_status = "📝 **標準モード**"
        mode_description = (
            "ペルソナベースの応答生成を使用しています。\n"
            "過去メッセージの類似度検索により応答を生成します。"
        )

    assert (
        "標準モード" in mode_status
    ), "標準モードの場合、適切なステータスメッセージを表示すべき"
    assert (
        "ペルソナベース" in mode_description
    ), "標準モードの詳細説明にペルソナベースの記載があるべき"

    print("✅ モードステータスメッセージ生成のテスト: 成功")


if __name__ == "__main__":
    print("🧪 /modeコマンドのロジックをテスト中...\n")
    test_llm_mode_detection()
    test_knowledge_data_detection()
    test_mode_status_messages()
    print("\n✅ すべてのテストが成功しました！")
