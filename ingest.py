import os
import hashlib
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    PointIdsList
)
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "docs"
DOC_FOLDER = "example_docs"

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def hash_content(text):
    """Generate SHA256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    local_files = {f for f in os.listdir(folder) if f.endswith(".txt")}

    # Ambil semua point dari Qdrant
    points, _ = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        with_payload=True,
        limit=10000
    )

    # Bangun map filename -> (point_id, content_hash)
    existing_sources = {}
    for point in points:
        source = point.payload.get("source")
        content_hash = point.payload.get("content_hash")
        if source and content_hash:
            existing_sources[source] = (point.id, content_hash)

    deleted = 0
    new_documents = 0

    for filename in local_files:
        file_path = os.path.join(folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content_hash = hash_content(content)

        if filename in existing_sources:
            point_id, old_hash = existing_sources[filename]

            if content_hash == old_hash:
                print(f"SKIP: {filename} already in Qdrant with same content.")
                continue
            else:
                # Delete old version
                qdrant.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=PointIdsList(points=[point_id])
                )
                print(f"UPDATED: {filename} content changed, re-ingesting.")
                deleted += 1
        else:
            print(f"NEW: {filename} not in Qdrant, ingesting.")

        embedding = model.encode(content).tolist()

        point = PointStruct(
            id=uuid4().hex,
            vector=embedding,
            payload={
                "text": content,
                "source": filename,
                "content_hash": content_hash
            }
        )

        qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])
        new_documents += 1

    # Hapus dokumen di Qdrant yang tidak ada lagi di lokal
    local_files_set = set(local_files)
    qdrant_sources_set = set(existing_sources.keys())

    files_to_delete = qdrant_sources_set - local_files_set

    for filename in files_to_delete:
        point_id, _ = existing_sources[filename]
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=PointIdsList(points=[point_id])
        )
        print(f"DELETED: {filename} no longer exists locally.")
        deleted += 1

    if deleted == 0 and new_documents == 0:
        print("No changes needed. Everything is up to date.")
    else:
        print(f"Finished. New: {new_documents}, Updated/Deleted: {deleted}")


if __name__ == "__main__":
    create_collection_if_not_exists()
    ingest_documents()