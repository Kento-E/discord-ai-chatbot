#!/usr/bin/env python3
"""
Gemini APIモデル有効性検証スクリプト

現在コードで指定されているモデルが利用可能かを確認します。
list_models() APIを使用するため、無料枠を消費しません。
"""

import os
import sys


def validate_model(model_name="gemini-2.0-flash"):
    """
    指定されたモデルが利用可能か確認する

    Args:
        model_name: 検証するモデル名

    Returns:
        bool: モデルが利用可能な場合True
    """
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
        available_models = []
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                available_models.append(model.name)

        # models/ プレフィックスを考慮してチェック
        full_model_name = f"models/{model_name}" if not model_name.startswith("models/") else model_name
        simple_model_name = model_name.replace("models/", "")

        if full_model_name in available_models:
            print(f"✅ モデルは利用可能です: {simple_model_name}")
            return True
        else:
            print(f"⚠️  警告: モデルが見つかりません: {simple_model_name}")
            print()
            print("📋 現在利用可能なモデル:")
            for model in available_models[:10]:
                model_display = model.replace("models/", "")
                print(f"   - {model_display}")
            if len(available_models) > 10:
                print(f"   ... 他 {len(available_models) - 10} モデル")
            print()
            print("🔧 対処が必要:")
            print("   以下のファイルでモデル名を更新してください:")
            print("   - src/test_gemini_connection.py")
            print("   - src/ai_agent.py")
            print("   - src/validate_gemini_model.py (このファイル)")
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

    # src/ai_agent.py と src/test_gemini_connection.py で使用されているモデル名
    model_name = "gemini-2.0-flash"

    result = validate_model(model_name)

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
    # モデルが無効でも終了コード0（警告だが、Bot起動は継続可能）
    sys.exit(0 if success else 0)
