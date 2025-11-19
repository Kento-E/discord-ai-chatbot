import json
import os
import random
import re
from sentence_transformers import SentenceTransformer, util

EMBED_PATH = os.path.join(os.path.dirname(__file__), '../data/embeddings.json')
PERSONA_PATH = os.path.join(os.path.dirname(__file__), '../data/persona.json')
model = SentenceTransformer('all-MiniLM-L6-v2')

# 埋め込みデータのロード
with open(EMBED_PATH, 'r') as f:
    dataset = json.load(f)

texts = [item['text'] for item in dataset]
embeddings = [item['embedding'] for item in dataset]

# ペルソナデータのロード
persona = None
if os.path.exists(PERSONA_PATH):
    with open(PERSONA_PATH, 'r') as f:
        persona = json.load(f)

# ユーザーの質問に最も近いメッセージを検索

def search_similar_message(query, top_k=3):
    query_emb = model.encode(query)
    scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = scores.argsort(descending=True)[:top_k]
    return [texts[i] for i in top_results]

# 予測される返信を生成

def generate_response(query, top_k=5):
    """
    クエリに対して、過去の知識とペルソナに基づいた予測返信を生成
    
    Args:
        query: ユーザーからの入力メッセージ
        top_k: 参考にする類似メッセージの数
    
    Returns:
        生成された返信文字列
    """
    # 類似メッセージを検索
    similar_messages = search_similar_message(query, top_k)
    
    # 類似メッセージが見つからない場合
    if not similar_messages:
        return "わかりません。"
    
    if not persona:
        # ペルソナがない場合は、類似メッセージをそのまま返す
        return similar_messages[0]
    
    # 入力の分析
    query_lower = query.lower()
    is_question = any(q in query_lower for q in ['？', '?', 'ですか', 'ますか', 'なに', '何', 'どう', 'いつ', 'どこ', 'だれ', '誰'])
    is_greeting = any(g in query_lower for g in ['おはよう', 'こんにちは', 'こんばんは', 'お疲れ'])
    
    # 挨拶への応答
    if is_greeting:
        greetings = persona.get('sample_greetings', [])
        if greetings:
            response = random.choice(greetings)
            return response
    
    # 質問への応答生成
    if is_question:
        # 最も類似度の高いメッセージを基に応答を構築
        base_message = similar_messages[0]
        
        # ペルソナの文末表現を使用
        common_endings = persona.get('common_endings', [])
        if common_endings:
            # 既存の文末を置き換え
            base_without_ending = re.sub(r'[。！？\s]+$', '', base_message)
            endings_subset = common_endings[:5] if len(common_endings) >= 5 else common_endings
            common_ending = random.choice(endings_subset)
            response = base_without_ending + common_ending
        else:
            response = base_message
        
        return response
    
    # 通常の会話応答
    # 複数の類似メッセージから要素を組み合わせる
    base_message = similar_messages[0]
    
    # メッセージの長さをペルソナの平均に近づける
    target_length = persona.get('avg_message_length', 50)
    
    if len(base_message) > target_length * 1.5:
        # 長すぎる場合は短縮
        sentences = [s for s in re.split(r'[。！？]', base_message) if s.strip()]
        response = (sentences[0] + '。') if sentences else base_message
    elif len(base_message) < target_length * 0.5:
        # 短すぎる場合は、2つ目の類似メッセージも参考にする
        if len(similar_messages) > 1:
            response = base_message + ' ' + similar_messages[1]
        else:
            response = base_message
    else:
        response = base_message
    
    # ペルソナの文末表現を適用
    common_endings = persona.get('common_endings', [])
    if common_endings:
        response = re.sub(r'[。！？\s]+$', '', response)
        endings_subset = common_endings[:5] if len(common_endings) >= 5 else common_endings
        common_ending = random.choice(endings_subset)
        response = response + common_ending
    
    return response

# テスト用
if __name__ == '__main__':
    q = input('質問を入力してください: ')
    
    # 類似メッセージの表示
    print('\n--- 類似メッセージ ---')
    results = search_similar_message(q)
    for r in results:
        print('-', r)
    
    # 予測返信の生成
    print('\n--- 予測される返信 ---')
    response = generate_response(q)
    print(response)
