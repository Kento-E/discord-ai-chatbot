"""
エラーメッセージの詳細表示機能のテスト
"""

import unittest
from unittest.mock import patch

from llm_error_handler import handle_gemini_exception, should_retry_with_backoff


class TestErrorMessages(unittest.TestCase):
    """エラーメッセージの詳細表示をテスト"""

    def test_handle_authentication_error(self):
        """認証エラーの処理をテスト"""
        error = Exception("InvalidArgument: API key is invalid")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertFalse(should_retry)
        self.assertEqual(error_type, "認証エラー")
        self.assertIn("APIキー", user_message)
        self.assertIn("GEMINI_API_KEY", user_message)

    def test_handle_rate_limit_error(self):
        """レート制限エラーの処理をテスト"""
        error = Exception("ResourceExhausted: Rate limit exceeded")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertTrue(should_retry)
        self.assertEqual(error_type, "レート制限")
        self.assertIn("制限", user_message)
        self.assertIn("待って", user_message)

    def test_handle_timeout_error(self):
        """タイムアウトエラーの処理をテスト"""
        error = Exception("DeadlineExceeded: Request timeout")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertTrue(should_retry)
        self.assertEqual(error_type, "タイムアウト")
        self.assertIn("時間", user_message)

    def test_handle_permission_error(self):
        """権限エラーの処理をテスト"""
        error = Exception("PermissionDenied: Access denied")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertFalse(should_retry)
        self.assertEqual(error_type, "権限エラー")
        self.assertIn("権限", user_message)

    def test_handle_content_filter_error(self):
        """コンテンツフィルターエラーの処理をテスト"""
        error = Exception("Response blocked by safety filters")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertFalse(should_retry)
        self.assertEqual(error_type, "コンテンツフィルター")
        self.assertIn("フィルター", user_message)

    def test_handle_unknown_error(self):
        """未知のエラーの処理をテスト"""
        error = Exception("Unknown error: Something went wrong")
        should_retry, error_type, user_message = handle_gemini_exception(error)

        self.assertFalse(should_retry)
        self.assertEqual(error_type, "不明なエラー")
        self.assertIn("Exception", user_message)
        self.assertIn("Something went wrong", user_message)

    def test_should_retry_with_backoff_returns_user_message(self):
        """should_retry_with_backoffがユーザーメッセージを返すかテスト"""
        error = Exception("ResourceExhausted")
        should_retry, wait_time, user_message = should_retry_with_backoff(
            error, 0
        )

        self.assertTrue(should_retry)
        self.assertGreater(wait_time, 0)
        self.assertIsNotNone(user_message)
        self.assertIsInstance(user_message, str)
        self.assertGreater(len(user_message), 0)

    def test_should_retry_with_backoff_max_retries(self):
        """最大リトライ回数に達した場合のテスト"""
        from llm_error_handler import MAX_RETRIES

        error = Exception("ResourceExhausted")
        should_retry, wait_time, user_message = should_retry_with_backoff(
            error, MAX_RETRIES
        )

        self.assertFalse(should_retry)
        self.assertEqual(wait_time, 0)
        self.assertIn("最大リトライ", user_message)


class TestGenerateResponseWithLLMErrorHandling(unittest.TestCase):
    """generate_response_with_llmのエラーハンドリングをテスト"""

    @patch("ai_agent.os.environ.get")
    def test_no_api_key_returns_none_tuple(self, mock_env):
        """APIキーが設定されていない場合のテスト"""
        mock_env.return_value = None

        from ai_agent import generate_response_with_llm

        result, error = generate_response_with_llm("test query", ["msg1"])

        self.assertIsNone(result)
        self.assertIsNone(error)

    def test_generate_response_handles_errors_correctly(self):
        """generate_responseがエラーを適切に処理するかテスト"""
        # このテストは統合テストなので、詳細な動作確認は手動で行う
        # ここでは、関数が存在し、適切なシグネチャを持つことのみ確認
        from ai_agent import generate_response

        # 関数が存在することを確認
        self.assertTrue(callable(generate_response))

        # 実際のAPI呼び出しを伴うテストは手動で行う


if __name__ == "__main__":
    unittest.main()
