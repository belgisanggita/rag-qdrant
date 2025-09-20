import os
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    PointIdsList
)
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "docs"
DOC_FOLDER = "example_docs"

# Init Qdrant client and embedding model
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

def ingest_documents(folder=DOC_FOLDER):
    # Ambil semua file .txt yang ada di folder lokal
    local_files = {f for f in os.listdir(folder) if f.endswith(".txt")}

    # Ambil semua dokumen yang sudah di-ingest ke Qdrant
    points, _ = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        with_payload=True,
        limit=10000  # Ubah sesuai jumlah dokumen
    )

    # Buat mapping source filename -> point_id dari Qdrant
    existing_sources = {}
    for point in points:
        source = point.payload.get("source")
        if source:
            existing_sources[source] = point.id

    # 1️⃣ DELETE dokumen dari Qdrant jika file-nya sudah tidak ada
    deleted = 0
    for source, point_id in existing_sources.items():
        if source not in local_files:
            qdrant.delete(
                collection_name=COLLECTION_NAME,
                points_selector=PointIdsList(points=[point_id])
            )
            print(f"DELETED from Qdrant: {source}")
            deleted += 1

    # 2️⃣ INGEST file baru yang belum ada
    new_documents = []
    for filename in local_files:
        if filename in existing_sources:
            print(f"SKIP: {filename} already in Qdrant.")
            continue

        file_path = os.path.join(folder, filename)

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

    if deleted == 0 and not new_documents:
        print("No changes needed. Everything is up to date.")

if __name__ == "__main__":
    create_collection_if_not_exists()
    ingest_documents()