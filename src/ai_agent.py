"""
AIエージェントモジュール

このモジュールは遅延ロード（Lazy Loading）を使用して、起動時間を最適化しています。
モデルとデータは初回の関数呼び出し時にロードされ、以降はキャッシュが使用されます。

実装の詳細:
- sentence_transformersライブラリは初回呼び出し時にインポート
- SentenceTransformerモデルは初回呼び出し時にロード
- 埋め込みデータとペルソナデータは初回呼び出し時にロード
- 2回目以降の呼び出しではキャッシュされたデータを使用

この設計により、モジュールのインポートは即座に完了し、
Bot起動時間が大幅に短縮されます。
"""

import json
import os
import random
import re
import threading

from gemini_config import get_model_name

EMBED_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")
PERSONA_PATH = os.path.join(os.path.dirname(__file__), "../data/persona.json")
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "../config/prompts.yaml")

# 遅延ロード用のグローバル変数（キャッシュ）
_model = None
_texts = None
_embeddings = None
_persona = None
_prompts = None
_gemini_model = None  # Gemini APIモデルのキャッシュ
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
    global _model, _texts, _embeddings, _persona, _initialized

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

            # ペルソナデータのロード
            if os.path.exists(PERSONA_PATH):
                with open(PERSONA_PATH, "r") as f:
                    _persona = json.load(f)

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
    global _model, _texts, _embeddings, _persona, _initialized

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

            # ペルソナデータのロード
            if os.path.exists(PERSONA_PATH):
                with open(PERSONA_PATH, "r") as f:
                    _persona = json.load(f)

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

    Returns:
        dict: プロンプト設定
    """
    global _prompts
    if _prompts is None:
        prompts_path = os.path.abspath(PROMPTS_PATH)
        if os.path.exists(prompts_path):
            import yaml

            with open(prompts_path, "r", encoding="utf-8") as f:
                _prompts = yaml.safe_load(f)
        else:
            # デフォルト値
            _prompts = {
                "llm_system_prompt": "あなたは過去のDiscordメッセージから学習した"
                "AIアシスタントです。\n以下の過去メッセージを参考に、"
                "ユーザーの質問に自然な日本語で回答してください。",
                "llm_response_instruction": "過去メッセージのスタイルを参考にしつつ、"
                "自然で簡潔な回答を生成してください。",
                "llm_context_header": "【過去メッセージ】",
                "llm_query_header": "【ユーザーの質問】",
                "llm_response_header": "【回答】",
            }
    return _prompts


def generate_response_with_llm(query, similar_messages):
    """
    LLM APIを使用して、過去メッセージを文脈として応答を生成

    Args:
        query: ユーザーからの入力メッセージ
        similar_messages: 類似度の高いメッセージのリスト

    Returns:
        LLMが生成した応答文字列、またはNone（API使用不可の場合）
    """
    global _gemini_model

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
        # (起動時のモード表示で既に案内済み)
        return None

    # google.generativeaiを遅延インポート（API使用時のみ）
    import google.generativeai as genai

    # APIの設定
    genai.configure(api_key=api_key)

    # モデルのインスタンスをキャッシュして再利用（パフォーマンス向上）
    if _gemini_model is None:
        _gemini_model = genai.GenerativeModel(get_model_name())

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
    for attempt in range(MAX_RETRIES + 1):
        try:
            # APIリクエスト（タイムアウトを明示的に設定）
            response = _gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                ),
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
                return result

            print("⚠️ LLM APIからの応答が空でした")
            print("   標準モード（ペルソナベース）にフォールバックします")
            log_llm_response(False)
            return None

        except Exception as e:
            # 例外を評価し、リトライすべきか判断
            should_retry, wait_time = should_retry_with_backoff(e, attempt)

            if should_retry:
                wait_for_retry(wait_time)
                continue
            else:
                # リトライ不可の場合はフォールバック
                # エラー内容をコンソールに出力して、問題を可視化
                print(f"⚠️ LLM API呼び出しに失敗: {type(e).__name__}: {str(e)}")
                print("   標準モード（ペルソナベース）にフォールバックします")
                log_llm_response(False)
                return None

    # 最大リトライ回数に達した場合
    print(f"⚠️ LLM API: 最大リトライ回数({MAX_RETRIES}回)に達しました")
    print("   標準モード（ペルソナベース）にフォールバックします")
    log_llm_response(False)
    return None


# ユーザーの質問に最も近いメッセージを検索


def search_similar_message(query, top_k=3):
    _ensure_initialized()
    # utilを遅延インポート
    from sentence_transformers import util

    query_emb = _model.encode(query)
    scores = util.cos_sim(query_emb, _embeddings)[0]
    top_results = scores.argsort(descending=True)[:top_k]
    return [_texts[i] for i in top_results]


# 予測される返信を生成


def generate_detailed_answer(similar_messages, persona):
    """
    質問に対して、複数の類似メッセージを組み合わせた詳細な回答を生成

    Args:
        similar_messages: 類似度の高いメッセージのリスト
        persona: ペルソナ情報

    Returns:
        詳細な回答文字列（複数行）
    """
    if not similar_messages:
        return "わかりません。"

    avg_length = persona.get("avg_message_length", 50)

    # 類似メッセージから文を抽出し、重複を避けながら組み合わせる
    response_parts = []
    used_sentences = set()
    target_length = max(avg_length * 3, 100)  # 質問には詳細に回答（最低100文字）
    current_length = 0  # 現在の長さを追跡

    for message in similar_messages:
        # メッセージを文に分割
        sentences = [s.strip() for s in re.split(r"[。！？]", message) if s.strip()]

        for sentence in sentences:
            # 重複チェック（類似度の高い文は除外）
            is_duplicate = False
            for used in used_sentences:
                # 60%以上一致する場合は重複とみなす（Jaccard類似度を使用）
                if len(sentence) > 0 and len(used) > 0:
                    set_sentence = set(sentence)
                    set_used = set(used)
                    intersection = len(set_sentence & set_used)
                    union = len(set_sentence | set_used)
                    similarity = intersection / union if union > 0 else 0
                    if similarity > 0.6:
                        is_duplicate = True
                        break

            if not is_duplicate and len(sentence) >= 3:
                response_parts.append(sentence)
                used_sentences.add(sentence)
                current_length += len(sentence)  # 長さを更新

                # 目標の長さに達したら終了
                if current_length >= target_length:
                    break

        # 十分な長さに達したら終了
        if current_length >= target_length:
            break

    # 最低2文は含めるようにする
    if len(response_parts) < 2 and len(similar_messages) >= 2:
        # 最初の2つのメッセージをそのまま使用
        response_parts = [similar_messages[0]]
        if len(similar_messages) > 1:
            response_parts.append(similar_messages[1])

    # 文を結合して回答を構築
    if not response_parts:
        response = similar_messages[0]
    else:
        # 各文を句点で終わらせる
        formatted_parts = []
        for part in response_parts:
            # 各文を句点で終わらせる
            if not re.search(r"[。！？]$", part):
                formatted_parts.append(part + "。")
            else:
                formatted_parts.append(part)

        response = "\n".join(formatted_parts)

    return response


def generate_casual_response(similar_messages, persona):
    """
    通常会話に対して、ペルソナに沿った短めの受け答えを生成

    Args:
        similar_messages: 類似度の高いメッセージのリスト
        persona: ペルソナ情報

    Returns:
        短めの自然な受け答え文字列
    """
    if not similar_messages:
        return "そうですね。"

    base_message = similar_messages[0]
    target_length = persona.get("avg_message_length", 50)

    # メッセージの長さをペルソナの平均に近づける
    if len(base_message) > target_length * 1.5:
        # 長すぎる場合は短縮（最初の文のみ）
        sentences = [s for s in re.split(r"[。！？]", base_message) if s.strip()]
        response = (sentences[0] + "。") if sentences else base_message
    elif len(base_message) < target_length * 0.5:
        # 短すぎる場合は、2つ目の類似メッセージも参考にする
        if len(similar_messages) > 1:
            second_message = similar_messages[1]
            # 2つ目のメッセージから最初の文を取得
            second_sentences = [
                s for s in re.split(r"[。！？]", second_message) if s.strip()
            ]
            if second_sentences:
                response = base_message + " " + second_sentences[0] + "。"
            else:
                response = base_message
        else:
            response = base_message
    else:
        response = base_message

    return response


def generate_response(query, top_k=5):
    """
    クエリに対して、過去の知識とペルソナに基づいた予測返信を生成

    Args:
        query: ユーザーからの入力メッセージ
        top_k: 参考にする類似メッセージの数

    Returns:
        生成された返信文字列
    """
    _ensure_initialized()

    # 類似メッセージを検索
    similar_messages = search_similar_message(query, top_k)

    # 類似メッセージが見つからない場合
    if not similar_messages:
        return "わかりません。"

    # LLM APIを試行（環境変数が設定されている場合）
    llm_response = generate_response_with_llm(query, similar_messages)
    if llm_response:
        return llm_response

    # フォールバック: LLM APIが使用できない場合は従来のロジックを使用
    if not _persona:
        # ペルソナがない場合は、類似メッセージをそのまま返す
        return similar_messages[0]

    # 入力の分析
    query_lower = query.lower()
    is_question = any(
        q in query_lower
        for q in [
            "？",
            "?",
            "ですか",
            "ますか",
            "なに",
            "何",
            "どう",
            "いつ",
            "どこ",
            "だれ",
            "誰",
            "どのように",
            "なぜ",
            "教えて",
            "方法",
            "やり方",
        ]
    )
    is_greeting = any(
        g in query_lower for g in ["おはよう", "こんにちは", "こんばんは", "お疲れ"]
    )

    # 挨拶への応答
    if is_greeting:
        greetings = _persona.get("sample_greetings", [])
        if greetings:
            response = random.choice(greetings)
            return response

    # 質問への応答生成（複数行の詳細な回答を構築）
    if is_question:
        return generate_detailed_answer(similar_messages, _persona)

    # 通常の会話応答（ペルソナに沿った短めの受け答え）
    return generate_casual_response(similar_messages, _persona)


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
