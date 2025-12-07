#!/usr/bin/env python3
"""
Gemini API疎通テストスクリプト

GEMINI_API_KEYの有効性を検証します。
"""

import os
import sys


def test_gemini_api_key():
    """Gemini APIキーの存在と有効性を確認する"""

    # 環境変数の取得
    api_key = os.environ.get("GEMINI_API_KEY")

    # 環境変数の存在確認
    if not api_key:
        print("⚠️ GEMINI_API_KEY が設定されていません")
        print("   標準モード（ペルソナベース）で動作します")
        return True  # 設定されていなくても正常（オプション）

    if not api_key.strip():
        print("⚠️ GEMINI_API_KEY が空です")
        print("   標準モード（ペルソナベース）で動作します")
        return True  # 空でも正常（オプション）

    print("📝 環境変数の確認:")
    print(f"  - GEMINI_API_KEY: 設定済み (長さ: {len(api_key)})")
    print()

    # Gemini APIへの疎通テスト
    print("🔄 Gemini APIへの接続を試みています...")

    try:
        # google-generativeaiライブラリをインポート
        import google.generativeai as genai

        # APIキーを設定
        genai.configure(api_key=api_key)

        # モデルを初期化（軽量なgemini-1.5-flashを使用）
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 簡単なテストメッセージを送信
        print("🧪 テストメッセージを送信しています...")
        response = model.generate_content(
            "こんにちは。APIテストです。「OK」とだけ返信してください。",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10,  # 最小限のトークン数
                temperature=0.1,  # 決定論的な応答
            ),
        )

        if response and response.text:
            print("✅ Gemini API接続成功: API認証完了")
            print(f"   応答: {response.text.strip()[:50]}")
            print()
            print("🎉 Gemini API疎通テストに成功しました！")
            print("   LLMモードが有効になります")
            return True
        else:
            print("❌ エラー: APIからの応答が空です")
            return False

    except ImportError as e:
        print("❌ エラー: google-generativeaiライブラリがインストールされていません")
        print(f"   詳細: {e}")
        print()
        print("   以下のコマンドでインストールしてください:")
        print("   pip install google-generativeai")
        return False

    except Exception as e:
        error_message = str(e)
        print("❌ エラー: Gemini APIへの接続に失敗しました")
        print(f"   詳細: {error_message}")
        print()

        # エラーメッセージに基づいて詳細なガイダンスを提供
        if "API_KEY_INVALID" in error_message or "invalid" in error_message.lower():
            print("   原因: APIキーが無効です")
            print("   対処: 正しいAPIキーを設定してください")
            print()
            print("   APIキーの取得方法:")
            print("   1. https://aistudio.google.com/ にアクセス")
            print("   2. Googleアカウントでログイン")
            print("   3. 'Get API Key'をクリック")
            print("   4. 新しいAPIキーを作成")

        elif "quota" in error_message.lower() or "429" in error_message:
            print("   原因: APIのレート制限に達しました")
            print("   対処: しばらく待ってから再試行してください")

        elif "permission" in error_message.lower() or "403" in error_message:
            print("   原因: APIへのアクセス権限がありません")
            print("   対処: APIキーの権限を確認してください")

        else:
            print("   原因: 予期しないエラーが発生しました")
            print("   対処: インターネット接続を確認してください")

        return False


def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("Gemini API疎通テスト")
    print("=" * 60 + "\n")

    result = test_gemini_api_key()

    print("\n" + "=" * 60)
    print("テスト結果")
    print("=" * 60 + "\n")

    if result:
        print("✅ 疎通テストに成功しました")
        return True
    else:
        print("❌ 疎通テストに失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
