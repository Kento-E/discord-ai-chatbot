#!/usr/bin/env python3
"""
Gemini APIモデル設定を読み込むモジュール

プロジェクト全体で使用するGeminiモデル名を一元管理します。
"""

import os
import yaml


# デフォルトのモデル名（設定ファイルが読み込めない場合のフォールバック）
DEFAULT_MODEL_NAME = "gemini-2.0-flash-lite"

# 設定ファイルのパス
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "gemini_model.yaml"
)


def get_model_name():
    """
    設定ファイルからGemini APIモデル名を取得する
    
    Returns:
        str: モデル名（例: "gemini-2.0-flash-lite"）
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get("model_name", DEFAULT_MODEL_NAME)
    except FileNotFoundError:
        # 設定ファイルが見つからない場合はデフォルト値を返す
        return DEFAULT_MODEL_NAME
    except Exception:
        # その他のエラーの場合もデフォルト値を返す
        return DEFAULT_MODEL_NAME


# モジュールレベルで定数として公開
GEMINI_MODEL_NAME = get_model_name()


if __name__ == "__main__":
    print(f"現在のGemini APIモデル: {GEMINI_MODEL_NAME}")
