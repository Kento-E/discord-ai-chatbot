"""
AIエージェントモジュール

このモジュールは遅延ロード（Lazy Loading）を使用して、起動時間を最適化しています。
モデルとデータは初回の関数呼び出し時にロードされ、以降はキャッシュが使用されます。

実装の詳細:
- sentence_transformersライブラリは初回呼び出し時にインポート
- SentenceTransformerモデルは初回呼び出し時にロード
- 埋め込みデータは初回呼び出し時にロード
- 2回目以降の呼び出しではキャッシュされたデータを使用

この設計により、モジュールのインポートは即座に完了し、
Bot起動時間が大幅に短縮されます。
"""

import json
import os
import threading

from gemini_config import create_generative_model

EMBED_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "../config/prompts.yaml")

# 遅延ロード用のグローバル変数（キャッシュ）
_model = None
_texts = None
_embeddings = None
_prompts = None
_cached_additional_role = None  # キャッシュされた追加役割の値
_gemini_model = None  # Gemini APIモデルのキャッシュ
_gemini_module = None  # genaiモジュールのキャッシュ
_safety_settings = None  # 安全性設定のキャッシュ
_llm_first_success = False  # LLM初回成功フラグ
_initialized = False
_init_lock = threading.Lock()
_llm_success_lock = threading.Lock()  # LLM成功メッセージ表示用ロック


def is_initialized():
    """
    初期化済みかどうかを返す

    Returns:
        bool: 初期化済みの場合True、未初期化の場合False
    """
    return _initialized


def ensure_initialized_with_callback(callback=None):
    """
    初期化を実行し、コールバックを通じて初回初期化かどうかを通知する

    この関数は初期化処理を実行し、初回の初期化時のみコールバックを呼び出します。
    2回目以降の呼び出しでは何もせず、即座にTrueを返します。

    Args:
        callback: 初回初期化時に呼び出される関数（引数なし）

    Returns:
        bool: 既に初期化済みだった場合True、今回初めて初期化した場合False

    Raises:
        FileNotFoundError: EMBED_PATHが存在しない場合
        json.JSONDecodeError: JSONファイルの解析に失敗した場合
        Exception: モデルのロードに失敗した場合
    """
    global _model, _texts, _embeddings, _initialized

    # 既に初期化済み
    if _initialized:
        return True

    # ダブルチェックロッキングパターン
    with _init_lock:
        # ロック取得後に再度チェック
        if _initialized:
            return True

        # 初回初期化開始
        if callback:
            callback()

        try:
            # sentence_transformersを遅延インポート（起動時間の最適化）
            from sentence_transformers import SentenceTransformer

            # モデルのロード
            _model = SentenceTransformer("all-MiniLM-L6-v2")

            # 埋め込みデータのロード
            if not os.path.exists(EMBED_PATH):
                raise FileNotFoundError(
                    f"埋め込みデータが見つかりません: {EMBED_PATH}\n"
                    "prepare_dataset.pyを実行してデータを生成してください。"
                )

            with open(EMBED_PATH, "r") as f:
                dataset = json.load(f)

            _texts = [item["text"] for item in dataset]
            _embeddings = [item["embedding"] for item in dataset]

            _initialized = True
            return False  # 初回初期化完了
        except json.JSONDecodeError as e:
            raise Exception(f"JSONファイルの解析に失敗しました: {str(e)}") from e
        except Exception as e:
            raise Exception(f"AIエージェントの初期化に失敗しました: {str(e)}") from e


def _ensure_initialized():
    """
    モデルとデータを遅延ロードする（初回呼び出し時のみ実行）

    スレッドセーフな実装により、複数の同時呼び出しでも安全に初期化されます。
    ダブルチェックロッキングパターンを使用して、パフォーマンスを最適化しています。

    Raises:
        FileNotFoundError: EMBED_PATHが存在しない場合
        json.JSONDecodeError: JSONファイルの解析に失敗した場合
        Exception: モデルのロードに失敗した場合
    """
    global _model, _texts, _embeddings, _initialized

    # 初期チェック（ロックなし）- パフォーマンス最適化
    if _initialized:
        return

    # ダブルチェックロッキングパターン
    with _init_lock:
        # ロック取得後に再度チェック
        if _initialized:
            return

        try:
            # sentence_transformersを遅延インポート（起動時間の最適化）
            from sentence_transformers import SentenceTransformer

            # モデルのロード
            _model = SentenceTransformer("all-MiniLM-L6-v2")

            # 埋め込みデータのロード
            if not os.path.exists(EMBED_PATH):
                raise FileNotFoundError(
                    f"埋め込みデータが見つかりません: {EMBED_PATH}\n"
                    "prepare_dataset.pyを実行してデータを生成してください。"
                )

            with open(EMBED_PATH, "r") as f:
                dataset = json.load(f)

            _texts = [item["text"] for item in dataset]
            _embeddings = [item["embedding"] for item in dataset]

            _initialized = True
        except FileNotFoundError:
            raise
        except json.JSONDecodeError as e:
            raise Exception(f"JSONファイルの解析に失敗しました: {str(e)}") from e
        except Exception as e:
            raise Exception(f"AIエージェントの初期化に失敗しました: {str(e)}") from e


def _load_prompts():
    """
    プロンプト設定をファイルから読み込む（キャッシュあり）

    環境変数 ADDITIONAL_AGENT_ROLE が設定されている場合、
    その内容をシステムプロンプトに追加します。
    ただし、環境変数が空文字列または空白のみの場合は無視されます。

    環境変数が変更された場合、キャッシュは自動的に無効化され、
    新しい値が反映されます。

    Returns:
        dict: プロンプト設定

    Raises:
        FileNotFoundError: prompts.yamlが存在しない場合
        RuntimeError: YAML構文エラーがある場合
    """
    global _prompts, _cached_additional_role

    # 環境変数の現在の値を取得
    current_additional_role = os.environ.get("ADDITIONAL_AGENT_ROLE", "").strip()

    # 環境変数が変更された場合はキャッシュを無効化
    if _prompts is not None and _cached_additional_role != current_additional_role:
        _prompts = None
        print("🔄 追加の役割設定が変更されました。プロンプトを再読み込みします")

    if _prompts is None:
        prompts_path = os.path.abspath(PROMPTS_PATH)
        if not os.path.exists(prompts_path):
            raise FileNotFoundError(
                f"プロンプト設定ファイルが見つかりません: {prompts_path}\n"
                "config/prompts.yamlを配置してください。"
            )

        import yaml

        try:
            with open(prompts_path, "r", encoding="utf-8") as f:
                _prompts = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(
                f"プロンプト設定ファイル（{prompts_path}）のYAML構文に誤りがあります。\n"
                f"エラー内容: {e}"
            ) from e

        # 環境変数から追加の役割指定を読み込む
        if current_additional_role and _prompts:
            # システムプロンプトに追加の役割を統合
            if "llm_system_prompt" in _prompts:
                _prompts["llm_system_prompt"] = (
                    f"{_prompts['llm_system_prompt']}\n\n"
                    f"【追加の役割・性格】\n{current_additional_role}"
                )
                print("✅ 追加の役割設定が適用されました")

        # 現在の環境変数の値をキャッシュに保存
        _cached_additional_role = current_additional_role
    return _prompts


def generate_response_with_llm(query, similar_messages):
    """
    LLM APIを使用して、過去メッセージを文脈として応答を生成

    Args:
        query: ユーザーからの入力メッセージ
        similar_messages: 類似度の高いメッセージのリスト

    Returns:
        tuple: (response: str or None, error_message: str or None)
            - response: LLMが生成した応答文字列、またはNone（エラー時）
            - error_message: エラーメッセージ、またはNone（成功時）
    """
    global _gemini_model, _gemini_module, _safety_settings

    # エラーハンドラーを遅延インポート
    from llm_error_handler import (
        MAX_RETRIES,
        log_llm_request,
        log_llm_response,
        should_retry_with_backoff,
        wait_for_retry,
    )

    # 環境変数からAPIキーを取得
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        # APIキーが設定されていない場合はNoneを返す
        # (起動時に既に案内済み)
        return None, None

    # モデルのインスタンスをキャッシュして再利用（パフォーマンス向上）
    if _gemini_model is None:
        # Gemini APIモデルを作成
        _gemini_module, _gemini_model, _safety_settings = create_generative_model(
            api_key
        )

    # キャッシュから取得
    genai = _gemini_module
    safety_settings = _safety_settings

    # 文脈として過去メッセージを整形
    context = "\n".join([f"- {msg}" for msg in similar_messages[:5]])

    # プロンプト設定を読み込み
    prompts = _load_prompts()

    # プロンプトの構築（外部設定ファイルから読み込み）
    prompt = f"""{prompts['llm_system_prompt']}

{prompts['llm_context_header']}
{context}

{prompts['llm_query_header']}
{query}

{prompts['llm_response_header']}
{prompts['llm_response_instruction']}"""

    # リクエストをログに記録
    log_llm_request(query, len(similar_messages[:5]))

    # リトライループ
    last_error_message = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            # APIリクエスト（タイムアウトを明示的に設定）
            response = _gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                ),
                safety_settings=safety_settings,
                request_options={"timeout": 30},
            )

            if response and response.text:
                result = response.text.strip()
                log_llm_response(True, len(result))
                # 初回のLLM応答成功時にのみ確認メッセージを表示（スレッドセーフ）
                with _llm_success_lock:
                    global _llm_first_success
                    if not _llm_first_success:
                        print(
                            "✅ LLM API応答成功: Gemini APIを使用して応答を生成しています"
                        )
                        _llm_first_success = True
                return result, None

            error_msg = "LLM APIからの応答が空でした"
            print(f"⚠️ {error_msg}")
            log_llm_response(False)
            return None, error_msg

        except Exception as e:
            # 例外を評価し、リトライすべきか判断
            retry_info = should_retry_with_backoff(e, attempt)
            should_retry, wait_time, user_message = retry_info
            last_error_message = user_message

            if should_retry:
                wait_for_retry(wait_time)
                continue
            else:
                # リトライ不可の場合はエラーを返す
                error_msg = f"LLM API呼び出しに失敗: {type(e).__name__}: {str(e)}"
                print(f"⚠️ {error_msg}")
                log_llm_response(False)
                return None, user_message

    # 最大リトライ回数に達した場合
    error_msg = f"LLM API: 最大リトライ回数({MAX_RETRIES}回)に達しました"
    print(f"⚠️ {error_msg}")
    log_llm_response(False)
    return None, last_error_message if last_error_message else error_msg


# ユーザーの質問に最も近いメッセージを検索


def search_similar_message(query, top_k=3):
    _ensure_initialized()
    # utilを遅延インポート
    from sentence_transformers import util

    query_emb = _model.encode(query)
    scores = util.cos_sim(query_emb, _embeddings)[0]
    top_results = scores.argsort(descending=True)[:top_k]
    return [_texts[i] for i in top_results]


def generate_response(query, top_k=5):
    """
    クエリに対して、LLM APIを使用して過去の知識を基に返信を生成

    Args:
        query: ユーザーからの入力メッセージ
        top_k: 参考にする類似メッセージの数

    Returns:
        生成された返信文字列

    Raises:
        ValueError: GEMINI_API_KEYが設定されていない場合
    """
    _ensure_initialized()

    # APIキーの確認
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "GEMINI_API_KEYが設定されていません。\n"
            "GEMINI_API_KEY環境変数を設定してください。"
        )

    # 類似メッセージを検索
    similar_messages = search_similar_message(query, top_k)

    # 類似メッセージが見つからない場合
    if not similar_messages:
        raise ValueError(
            "関連する過去メッセージが見つかりませんでした。\n"
            "知識データが正しく生成されているか確認してください。"
        )

    # LLM APIを使用して応答を生成
    llm_response, error_message = generate_response_with_llm(query, similar_messages)
    if llm_response:
        return llm_response

    # LLM APIが失敗した場合
    if error_message:
        raise RuntimeError(f"LLM APIからの応答取得に失敗しました。\n{error_message}")
    else:
        raise RuntimeError(
            "LLM APIからの応答取得に失敗しました。\n"
            "APIキーが正しいか、ネットワーク接続を確認してください。"
        )


# テスト用
if __name__ == "__main__":
    q = input("質問を入力してください: ")

    # 類似メッセージの表示
    print("\n--- 類似メッセージ ---")
    results = search_similar_message(q)
    for r in results:
        print("-", r)

    # 予測返信の生成
    print("\n--- 予測される返信 ---")
    response = generate_response(q)
    print(response)
