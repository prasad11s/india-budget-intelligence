import json
import re

input_path = "data/processed/budget_at_a_glance.json"
output_path = "data/processed/budget_at_a_glance_clean.json"

devanagari_pattern = re.compile(r"[\u0900-\u097F]+")

with open(input_path, "r", encoding="utf-8") as f:
    doc = json.load(f)

for page in doc["pages"]:
    if page["text"]:
        text = devanagari_pattern.sub("", page["text"])
        lines = text.split("\n")
        lines = [line for line in lines if line.strip() != ""]
        text = "\n".join(lines)
        text = re.sub(r" {2,}", " ", text)
        page["text"] = text.strip()

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

print(f"Cleaned {len(doc['pages'])} pages, saved to {output_path}")