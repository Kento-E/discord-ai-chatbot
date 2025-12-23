#!/usr/bin/env python3
"""
Gemini APIモデル関連のユーティリティ関数

モデルの有効性確認やリスト表示などの共通機能を提供します。
"""


def list_available_models(genai):
    """
    利用可能なGeminiモデルの一覧を取得する

    Args:
        genai: google.generativeai モジュール

    Returns:
        list: generateContentをサポートするモデル名のリスト
    """
    available_models = []
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            available_models.append(model.name)
    return available_models


def print_available_models(available_models, max_display=10):
    """
    利用可能なモデルを表示する

    Args:
        available_models: モデル名のリスト
        max_display: 最大表示数
    """
    print("📋 現在利用可能なモデル:")
    for model in available_models[:max_display]:
        model_display = model.replace("models/", "")
        print(f"   - {model_display}")
    if len(available_models) > max_display:
        print(f"   ... 他 {len(available_models) - max_display} モデル")


def print_update_instructions():
    """モデル名の更新が必要な場合の指示を表示する"""
    print()
    print("🔧 対処が必要:")
    print("   以下のファイルでモデル名を更新してください:")
    print("   - src/test_gemini_connection.py")
    print("   - src/ai_chatbot.py")
    print("   - src/validate_gemini_model.py")
