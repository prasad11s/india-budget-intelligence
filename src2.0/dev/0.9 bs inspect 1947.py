import configparser
import chromadb

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"


def main():
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    result = collection.get(
        where={"year": {"$in": ["194748", "1947_48"]}},
        include=["documents", "metadatas"],
    )

    print(f"Total chunks found for 1947-48: {len(result['ids'])}\n")
    for cid, doc, meta in zip(result["ids"], result["documents"], result["metadatas"]):
        print("=" * 80)
        print(f"id={cid}  page_start={meta.get('page_start')}  page_end={meta.get('page_end')}")
        print(doc)
        print()


if __name__ == "__main__":
    main()