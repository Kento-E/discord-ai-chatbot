#!/usr/bin/env python3
"""
Gemini APIモデル有効性検証スクリプト

現在コードで指定されているモデルが利用可能かを確認します。
list_models() APIを使用するため、無料枠を消費しません。
"""

import os
import sys

from gemini_config import get_model_name
from gemini_model_utils import (
    list_available_models,
    print_available_models,
    print_update_instructions,
)


def validate_model(model_name=None):
    """
    指定されたモデルが利用可能か確認する

    Args:
        model_name: 検証するモデル名（Noneの場合はconfig/gemini_model.tomlから取得、
                   設定ファイルが読み込めない場合はデフォルト値を使用）

    Returns:
        bool: モデルが利用可能な場合True
    """
    # モデル名が指定されていない場合は設定ファイルから取得
    if model_name is None:
        model_name = get_model_name()

    api_key = os.environ.get("GEMINI_API_KEY")

    # APIキーが設定されていない場合はスキップ
    if not api_key or not api_key.strip():
        print("ℹ️  GEMINI_API_KEY が設定されていません")
        print("   標準モード（ペルソナベース）で動作します")
        print("   モデル検証をスキップします")
        return True

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        print(f"🔍 モデルの有効性を確認中: {model_name}")

        # 利用可能なモデルを取得（無料枠を消費しない）
        available_models = list_available_models(genai)

        # models/ プレフィックスを考慮してチェック
        full_model_name = (
            f"models/{model_name}"
            if not model_name.startswith("models/")
            else model_name
        )
        simple_model_name = model_name.replace("models/", "")

        if full_model_name in available_models:
            print(f"✅ モデルは利用可能です: {simple_model_name}")
            return True
        else:
            print(f"⚠️  警告: モデルが見つかりません: {simple_model_name}")
            print()
            print_available_models(available_models, max_display=10)
            print_update_instructions()
            return False

    except ImportError:
        print("⚠️  google-generativeai ライブラリが見つかりません")
        print("   モデル検証をスキップします")
        return True

    except Exception as e:
        print(f"⚠️  モデル検証中にエラーが発生: {e}")
        print("   モデル検証をスキップします")
        return True  # エラーでも継続（主要機能ではない）


def main():
    """メイン関数"""
    print("\n" + "=" * 60)
    print("Gemini APIモデル有効性検証")
    print("=" * 60 + "\n")

    # 設定ファイルから現在使用されているモデル名を取得
    result = validate_model()

    print("\n" + "=" * 60)
    print("検証結果")
    print("=" * 60 + "\n")

    if result:
        print("✅ 検証完了")
        return True
    else:
        print("⚠️  モデルの更新が必要です")
        return False


if __name__ == "__main__":
    success = main()
    # モデルが無効な場合は終了コード1（警告を表示するが、Bot起動は継続）
    sys.exit(0 if success else 1)
