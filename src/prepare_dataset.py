import json
import os
from sentence_transformers import SentenceTransformer
from collections import Counter
import re

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/messages.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '../data/embeddings.json')
PERSONA_PATH = os.path.join(os.path.dirname(__file__), '../data/persona.json')

# メッセージデータの読み込み
with open(DATA_PATH, 'r') as f:
    messages = json.load(f)

# メッセージ本文のみ抽出
texts = [msg['content'] for msg in messages if msg['content'].strip()]

# 埋め込みモデル（無料で使えるall-MiniLM-L6-v2）
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)

# 埋め込みと元テキストを保存
output = [
    {'text': text, 'embedding': emb.tolist()}
    for text, emb in zip(texts, embeddings)
]

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"{len(output)}件のメッセージを埋め込み化し、{OUTPUT_PATH}に保存しました。")

# ペルソナの生成
def generate_persona(texts):
    """過去メッセージからペルソナ情報を生成"""
    # 基本統計
    total_messages = len(texts)
    avg_length = sum(len(text) for text in texts) / total_messages if total_messages > 0 else 0
    
    # 頻出単語の抽出（簡易的な形態素解析の代わりに単語分割）
    all_words = []
    for text in texts:
        # 日本語と英語の単語を抽出
        words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFFa-zA-Z]+', text)
        all_words.extend(words)
    
    common_words = Counter(all_words).most_common(50)
    
    # 文末表現の抽出
    sentence_endings = []
    for text in texts:
        # 文末の2-3文字を抽出
        if len(text) >= 2:
            endings = re.findall(r'[^。！？\n]{1,3}[。！？]?$', text)
            sentence_endings.extend(endings)
    
    common_endings = Counter(sentence_endings).most_common(20)
    
    # 挨拶表現の検出
    greetings = []
    greeting_patterns = [
        'おはよう', 'こんにちは', 'こんばんは', 'お疲れ', 'ありがとう',
        'よろしく', 'おやすみ', 'おつ', 'お願い', 'すみません'
    ]
    for text in texts:
        for pattern in greeting_patterns:
            if pattern in text:
                if len(text) > 50:
                    greetings.append(text[:50] + '...')
                else:
                    greetings.append(text)
                break
    
    # サンプルメッセージ（代表的なメッセージ）
    sample_messages = texts[:10] if len(texts) >= 10 else texts
    
    persona = {
        'total_messages': total_messages,
        'avg_message_length': round(avg_length, 2),
        'common_words': [word for word, count in common_words[:30]],
        'common_endings': [ending for ending, count in common_endings[:10]],
        'sample_greetings': greetings[:10],
        'sample_messages': sample_messages,
        'description': f'過去{total_messages}件のメッセージから学習したペルソナ。平均メッセージ長は{round(avg_length, 2)}文字。'
    }
    
    return persona

# ペルソナ生成と保存
persona = generate_persona(texts)
with open(PERSONA_PATH, 'w') as f:
    json.dump(persona, f, ensure_ascii=False, indent=2)

print(f"ペルソナ情報を{PERSONA_PATH}に保存しました。")
