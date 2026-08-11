import os

for doc_type in ["budget_speeches", "budget_documents", "economic_surveys"]:
    for root, dirs, files in os.walk(os.path.join("data/raw", doc_type)):
        for f in files:
            if f.lower().endswith(".pdf") and not f.endswith(".pdf"):
                print(f"{doc_type}: {os.path.join(root, f)}")