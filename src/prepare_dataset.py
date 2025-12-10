import json
import os

from sentence_transformers import SentenceTransformer

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/messages.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")

# メッセージデータの読み込み
with open(DATA_PATH, "r") as f:
    messages = json.load(f)

# メッセージ本文のみ抽出
texts = [msg["content"] for msg in messages if msg["content"].strip()]

# 埋め込みモデル（無料で使えるall-MiniLM-L6-v2）
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts, show_progress_bar=True)

# 埋め込みと元テキストを保存
output = [
    {"text": text, "embedding": emb.tolist()} for text, emb in zip(texts, embeddings)
]

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"{len(output)}件のメッセージを埋め込み化し、{OUTPUT_PATH}に保存しました。")
