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

EMBED_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")
PERSONA_PATH = os.path.join(os.path.dirname(__file__), "../data/persona.json")

# 遅延ロード用のグローバル変数（キャッシュ）
_model = None
_texts = None
_embeddings = None
_persona = None
_initialized = False
_init_lock = threading.Lock()


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


def _is_similar_sentence(sentence1, sentence2, threshold=0.6):
    """
    2つの文の類似度を判定（Jaccard類似度を使用）

    Args:
        sentence1: 比較する文1
        sentence2: 比較する文2
        threshold: 類似度の閾値（デフォルト0.6）

    Returns:
        bool: 類似度が閾値以上の場合True
    """
    if len(sentence1) == 0 or len(sentence2) == 0:
        return False

    set_sentence1 = set(sentence1)
    set_sentence2 = set(sentence2)
    intersection = len(set_sentence1 & set_sentence2)
    union = len(set_sentence1 | set_sentence2)
    similarity = intersection / union if union > 0 else 0

    return similarity > threshold


def _extract_actionable_sentences(message):
    """
    メッセージから実践的なアドバイス・アクションを含む文を抽出

    Args:
        message: 対象メッセージ

    Returns:
        (actionable_sentences, all_sentences): 実践的な文のリストと全ての文のリスト
    """
    # メッセージを文に分割
    sentences = [s.strip() for s in re.split(r"[。！？]", message) if s.strip()]

    # 実践的アドバイスを示すパターン
    actionable_patterns = [
        r"(して|する|した)ください",
        r"(して|する|した)方が良い",
        r"(して|する|した)といい",
        r"(する|した)方法",
        r"手順",
        r"やり方",
        r"ステップ",
        r"まず",
        r"次に",
        r"その後",
        r"最後に",
        r"必要",
        r"重要",
        r"確認",
        r"注意",
        r"ポイント",
        r"コツ",
        r"試して",
        r"おすすめ",
        r"推奨",
        r"できます",
        r"可能",
        r"使って",
        r"設定",
        r"インストール",
        r"実行",
        r"変更",
    ]

    actionable_sentences = []
    for sentence in sentences:
        # 実践的アドバイスのパターンにマッチするかチェック
        for pattern in actionable_patterns:
            if re.search(pattern, sentence):
                actionable_sentences.append(sentence)
                break

    return actionable_sentences, sentences


def _organize_advice_as_steps(advice_sentences):
    """
    アドバイスを手順として整理

    Args:
        advice_sentences: アドバイス文のリスト

    Returns:
        整理されたアドバイスリスト
    """
    if not advice_sentences:
        return []

    # 手順を示すキーワード
    step_keywords = ["まず", "次に", "その後", "最後に", "最初に", "1", "2", "3"]

    # 手順を示す文を優先的に配置
    step_sentences = []
    other_sentences = []

    for sentence in advice_sentences:
        is_step = False
        for keyword in step_keywords:
            if keyword in sentence:
                step_sentences.append(sentence)
                is_step = True
                break
        if not is_step:
            other_sentences.append(sentence)

    # 手順文を先に、その他を後に配置
    return step_sentences + other_sentences


def generate_detailed_answer(similar_messages, persona):
    """
    質問に対して、知識データから実践的なアドバイスを抽出して回答を生成

    Args:
        similar_messages: 類似度の高いメッセージのリスト
        persona: ペルソナ情報

    Returns:
        実践的なアドバイスを含む詳細な回答文字列
    """
    if not similar_messages:
        return "わかりません。"

    # 全メッセージから実践的アドバイスを抽出
    all_actionable = []
    all_sentences = []
    used_sentences = set()

    for message in similar_messages:
        actionable, sentences = _extract_actionable_sentences(message)
        all_actionable.extend(actionable)
        all_sentences.extend(sentences)

    # 重複を除去（Jaccard類似度で判定）
    unique_actionable = []
    for sentence in all_actionable:
        is_duplicate = any(
            _is_similar_sentence(sentence, used) for used in used_sentences
        )

        if not is_duplicate and len(sentence) >= 5:
            unique_actionable.append(sentence)
            used_sentences.add(sentence)

    # 実践的アドバイスが見つかった場合
    if unique_actionable:
        # 手順として整理
        organized_advice = _organize_advice_as_steps(unique_actionable)

        # 最大5つまでのアドバイスを含める
        advice_to_include = organized_advice[:5]

        # 各アドバイスを句点で終わらせる
        formatted_advice = []
        for advice in advice_to_include:
            if not re.search(r"[。！？]$", advice):
                formatted_advice.append(advice + "。")
            else:
                formatted_advice.append(advice)

        # 手順が複数ある場合は番号付きで返す
        if len(formatted_advice) >= 3:
            numbered_advice = []
            for i, advice in enumerate(formatted_advice, 1):
                numbered_advice.append(f"{i}. {advice}")
            return "\n".join(numbered_advice)
        else:
            return "\n".join(formatted_advice)

    # 実践的アドバイスがない場合は、通常の文から構築
    response_parts = []
    target_sentences = 3  # 最大3文

    for sentence in all_sentences:
        is_duplicate = any(
            _is_similar_sentence(sentence, used) for used in used_sentences
        )

        if not is_duplicate and len(sentence) >= 3:
            response_parts.append(sentence)
            used_sentences.add(sentence)

            if len(response_parts) >= target_sentences:
                break

    # 回答が空の場合は最初のメッセージを返す
    if not response_parts:
        return similar_messages[0]

    # 各文を句点で終わらせる
    formatted_parts = []
    for part in response_parts:
        if not re.search(r"[。！？]$", part):
            formatted_parts.append(part + "。")
        else:
            formatted_parts.append(part)

    return "\n".join(formatted_parts)


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
