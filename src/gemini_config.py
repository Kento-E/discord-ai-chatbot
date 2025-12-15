#!/usr/bin/env python3
"""
Gemini APIモデル設定を読み込むモジュール

プロジェクト全体で使用するGeminiモデル名を一元管理します。
遅延ロードを使用して、モジュールインポート時のオーバーヘッドを最小限に抑えます。
"""

import os

import yaml

# デフォルトのモデル名（設定ファイルが読み込めない場合のフォールバック）
DEFAULT_MODEL_NAME = "gemini-2.5-flash-lite"

# 設定ファイルのパス
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "gemini_model.yaml",
)

# 遅延ロード用のキャッシュ
_cached_model_name = None


def get_model_name():
    """
    設定ファイルからGemini APIモデル名を取得する（遅延ロード + キャッシュ）

    初回呼び出し時に設定ファイルを読み込み、結果をキャッシュします。
    2回目以降の呼び出しではキャッシュされた値を返します。

    設定ファイル（config/gemini_model.yaml）が存在し読み込める場合は
    そこからモデル名を取得します。ファイルが見つからない、または
    YAML解析エラーが発生した場合は、デフォルト値（DEFAULT_MODEL_NAME）を返します。

    Returns:
        str: モデル名（例: "gemini-2.5-flash-lite"）
             設定ファイルから取得できない場合はDEFAULT_MODEL_NAME
    """
    global _cached_model_name

    # キャッシュがある場合はそれを返す
    if _cached_model_name is not None:
        return _cached_model_name

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            _cached_model_name = config.get("model_name", DEFAULT_MODEL_NAME)
            return _cached_model_name
    except FileNotFoundError:
        # 設定ファイルが見つからない場合はデフォルト値を返す
        _cached_model_name = DEFAULT_MODEL_NAME
        return _cached_model_name
    except (yaml.YAMLError, PermissionError) as e:
        # YAML解析エラーまたは権限エラーの場合はデフォルト値を返す
        print(f"⚠️ 設定ファイルの読み込みに失敗: {e}")
        print(f"   デフォルトモデルを使用: {DEFAULT_MODEL_NAME}")
        _cached_model_name = DEFAULT_MODEL_NAME
        return _cached_model_name


def get_safety_settings(genai):
    """
    Gemini API用の安全性フィルター設定を取得する

    すべてのカテゴリで安全性フィルターを無効化（BLOCK_NONE）した設定を返します。

    Args:
        genai: google.generativeai モジュール

    Returns:
        dict: 安全性フィルター設定の辞書
    """
    HarmCategory = genai.types.HarmCategory
    HarmBlockThreshold = genai.types.HarmBlockThreshold
    return {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }


def create_generative_model(api_key):
    """
    Gemini APIモデルを作成する

    APIキーを使用してgenaiを設定し、安全性フィルター設定を適用した
    GenerativeModelインスタンスを作成して返します。

    Args:
        api_key: Gemini APIキー

    Returns:
        tuple: (genai, model, safety_settings)
            - genai: google.generativeai モジュール
            - model: GenerativeModel インスタンス
            - safety_settings: 安全性フィルター設定の辞書
    """
    import google.generativeai as genai

    # APIキーを設定
    genai.configure(api_key=api_key)

    # 安全性フィルター設定を取得
    safety_settings = get_safety_settings(genai)

    # モデルを作成
    model = genai.GenerativeModel(get_model_name(), safety_settings=safety_settings)

    return genai, model, safety_settings


if __name__ == "__main__":
    print(f"現在のGemini APIモデル: {get_model_name()}")
