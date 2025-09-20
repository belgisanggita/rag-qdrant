import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Load GROQ_API_KEY dari .env

COLLECTION_NAME = "docs"

# Init Qdrant dan embedding model
qdrant = QdrantClient(host="localhost", port=6333)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Init Groq client
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def search_similar_documents(query: str, top_k=3):
    query_vector = embedding_model.encode(query).tolist()
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload["text"] for hit in hits]

def generate_answer_with_groq(question: str, context: str):
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    chat_completion = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def generate_answer(question: str):
    documents = search_similar_documents(question)
    context = "\n".join(documents)
    answer = generate_answer_with_groq(question, context)
    return {
        "answer": answer,
        "context_used": context
    }