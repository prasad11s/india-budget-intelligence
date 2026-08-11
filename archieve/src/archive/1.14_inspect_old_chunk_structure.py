import json

with open("data/chunks/economic_surveys/1957-1958_chapters_1%20Stresses%20and%20Strains%20of%20Development.json", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Number of chunks in this file: {len(chunks)}")
print("\nFirst chunk's full structure:")
print(json.dumps(chunks[0], indent=2)[:1000])