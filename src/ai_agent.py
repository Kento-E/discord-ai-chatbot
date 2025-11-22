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


def apply_common_ending(base_text, common_endings):
    """
    メッセージに共通の語尾を適用する（重複を避ける）

    Args:
        base_text: 元のメッセージ
        common_endings: 適用可能な語尾のリスト

    Returns:
        語尾が適用されたメッセージ
    """
    if not common_endings:
        return base_text

    # 既存の文末句読点を除去
    text_without_ending = re.sub(r"[。！？\s]+$", "", base_text)
    # すべての語尾からランダムに選択
    common_ending = random.choice(common_endings)

    # 重複を避けるため、既に同じ語尾で終わっている場合は追加しない
    # common_endingから句読点を除いた部分を抽出
    ending_without_punct = re.sub(r"[。！？\s]+$", "", common_ending)
    if not ending_without_punct:
        # 純粋な句読点の語尾 - そのまま追加
        return text_without_ending + common_ending
    elif text_without_ending.endswith(ending_without_punct):
        # 既にこの語尾を持っている - 元のテキストを使用
        return base_text
    else:
        # 異なる語尾 - 置き換える
        return text_without_ending + common_ending


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

    common_endings = persona.get("common_endings", [])
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
        # 各文にペルソナの文末表現を適用
        formatted_parts = []
        for i, part in enumerate(response_parts):
            if i == len(response_parts) - 1:
                # 最後の文には文末表現を適用
                formatted_parts.append(apply_common_ending(part, common_endings))
            else:
                # 途中の文は句点で終わらせる
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
    common_endings = persona.get("common_endings", [])
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

    # ペルソナの文末表現を適用
    response = apply_common_ending(response, common_endings)

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
