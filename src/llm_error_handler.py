"""
LLM APIエラーハンドリングモジュール

このモジュールはLLM API呼び出し時の例外を適切に処理し、
ログ出力を行います。
"""

import logging
import time

# ロガーの設定
logger = logging.getLogger(__name__)

# リトライ設定
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
# MAX_BACKOFF_SECONDSはMAX_RETRIESから算出（最後のリトライ時の待機時間）
MAX_BACKOFF_SECONDS = INITIAL_BACKOFF_SECONDS * (2 ** (MAX_RETRIES - 1))


class LLMError(Exception):
    """LLM API関連のエラーの基底クラス"""


class LLMAuthenticationError(LLMError):
    """認証エラー（APIキーが無効など）"""


class LLMRateLimitError(LLMError):
    """レート制限エラー"""


class LLMTimeoutError(LLMError):
    """タイムアウトエラー"""


class LLMContentError(LLMError):
    """コンテンツ生成エラー（安全性フィルターなど）"""


def handle_gemini_exception(exception):
    """
    Gemini API例外を適切に処理し、ログ出力を行う

    Args:
        exception: 発生した例外

    Returns:
        tuple: (should_retry: bool, error_type: str, user_message: str)
    """
    exception_type = type(exception).__name__
    exception_message = str(exception)

    # google.generativeai の例外を分類
    if (
        "InvalidArgument" in exception_type
        or "invalid" in exception_message.lower()
        or "invalid api key" in exception_message.lower()
    ):
        logger.warning(f"LLM API認証エラー: APIキーが無効です - {exception_type}")
        return (
            False,
            "認証エラー",
            "APIキーが無効です。GEMINI_API_KEYの設定を確認してください。",
        )

    if (
        "ResourceExhausted" in exception_type
        or "ResourceExhausted" in exception_message
        or "429" in exception_message
        or "rate limit" in exception_message.lower()
    ):
        logger.warning(
            f"LLM APIレート制限: リクエスト制限に達しました - {exception_type}"
        )
        return (
            True,
            "レート制限",
            "APIのリクエスト制限に達しました。しばらく待ってから再度お試しください。",
        )

    if (
        "DeadlineExceeded" in exception_type
        or "DeadlineExceeded" in exception_message
        or "timeout" in exception_message.lower()
    ):
        logger.warning(f"LLM APIタイムアウト: 応答時間超過 - {exception_type}")
        return (
            True,
            "タイムアウト",
            "APIの応答時間が超過しました。ネットワーク接続を確認してください。",
        )

    if (
        "PermissionDenied" in exception_type
        or "PermissionDenied" in exception_message
        or "permission denied" in exception_message.lower()
    ):
        logger.warning(
            f"LLM API権限エラー: アクセス権限がありません - {exception_type}"
        )
        return (
            False,
            "権限エラー",
            "APIへのアクセス権限がありません。APIキーの権限設定を確認してください。",
        )

    if "blocked" in exception_message.lower() or "safety" in exception_message.lower():
        logger.info(
            f"LLM APIコンテンツフィルター: 応答がブロックされました - {exception_type}"
        )
        return (
            False,
            "コンテンツフィルター",
            "応答が安全性フィルターによりブロックされました。質問内容を変更してお試しください。",
        )

    # その他の例外
    logger.debug(f"LLM API例外: {exception_type} - {exception_message}")
    return (
        False,
        "不明なエラー",
        f"予期しないエラーが発生しました: {exception_type} - {exception_message}",
    )


def log_llm_request(query, context_count):
    """
    LLM APIリクエストをログに記録

    Args:
        query: ユーザーからの質問
        context_count: コンテキストとして渡したメッセージ数
    """
    logger.debug(f"LLM APIリクエスト: query長={len(query)}, context数={context_count}")


def log_llm_response(success, response_length=0):
    """
    LLM APIレスポンスをログに記録

    Args:
        success: 成功したかどうか
        response_length: レスポンスの長さ
    """
    if success:
        logger.debug(f"LLM API応答成功: response長={response_length}")
    else:
        logger.debug("LLM API応答なし: フォールバックを使用")


def calculate_backoff(attempt):
    """
    指数バックオフで待機時間を計算

    Args:
        attempt: リトライ回数（0から開始）

    Returns:
        float: 待機時間（秒）
    """
    backoff = min(INITIAL_BACKOFF_SECONDS * (2**attempt), MAX_BACKOFF_SECONDS)
    return backoff


def should_retry_with_backoff(exception, attempt):
    """
    例外を評価し、リトライすべきかと待機時間を返す

    Args:
        exception: 発生した例外
        attempt: 現在のリトライ回数

    Returns:
        tuple: (should_retry: bool, wait_seconds: float, user_message: str)
    """
    if attempt >= MAX_RETRIES:
        logger.warning(f"LLM API最大リトライ回数到達: {MAX_RETRIES}回")
        return False, 0, f"最大リトライ回数({MAX_RETRIES}回)に達しました。"

    should_retry, error_type, user_message = handle_gemini_exception(exception)

    if should_retry:
        wait_time = calculate_backoff(attempt)
        logger.info(
            f"LLM APIリトライ予定: {attempt + 1}/{MAX_RETRIES}回目, 待機時間={wait_time:.1f}秒"
        )
        return True, wait_time, user_message

    return False, 0, user_message


def wait_for_retry(wait_seconds):
    """
    リトライ前に待機

    Args:
        wait_seconds: 待機時間（秒）
    """
    if wait_seconds > 0:
        time.sleep(wait_seconds)
