import sys
import json
import glob
from openai import OpenAI

MODEL = sys.argv[1] if len(sys.argv) > 1 else "text-embedding-3-small"
SAMPLE_SIZE = 10

client = OpenAI()  # reads OPENAI_API_KEY from environment

files = glob.glob("data/chunks/budget_speeches/*.json")[:2]
chunks = []
for f in files:
    with open(f, encoding="utf-8") as file:
        chunks.extend(json.load(file))
chunks = chunks[:SAMPLE_SIZE]

texts = [c["text"] for c in chunks]
response = client.embeddings.create(model=MODEL, input=texts)

print(f"Model: {MODEL}")
print(f"Chunks embedded: {len(texts)}")
print(f"Vector dimensions: {len(response.data[0].embedding)}")
print(f"First chunk preview: {texts[0][:80]}...")