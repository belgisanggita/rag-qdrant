import os
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "docs"
DOC_FOLDER = "example_docs"

qdrant = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def create_collection_if_not_exists():
    collections = qdrant.get_collections().collections
    exists = any(col.name == COLLECTION_NAME for col in collections)

    if not exists:
        print("Collection not found. Creating...")
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    else:
        print("Collection already exists. Skipping creation.")

def document_already_ingested(file_name: str) -> bool:
    result = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=file_name))]
        ),
        limit=1,
    )
    return bool(result.points)

def ingest_documents(folder=DOC_FOLDER):
    new_documents = []
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue
        file_path = os.path.join(folder, filename)

        if document_already_ingested(filename):
            print(f"SKIP: {filename} already in Qdrant.")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        embedding = model.encode(content).tolist()

        point = PointStruct(
            id=uuid4().hex,
            vector=embedding,
            payload={"text": content, "source": filename}
        )
        new_documents.append(point)

    if new_documents:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=new_documents)
        print(f"INGESTED {len(new_documents)} new document(s).")
    else:
        print("No new documents to ingest.")

if __name__ == "__main__":
    create_collection_if_not_exists()
    ingest_documents()
