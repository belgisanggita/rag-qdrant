# RAG with Qdrant Vector Database

A Retrieval-Augmented Generation (RAG) system built with Qdrant vector database, Sentence Transformers for embeddings, and Groq LLM for answer generation. The system automatically monitors document changes and provides real-time document ingestion capabilities.

## Features

- **Document Ingestion**: Automatic processing and vectorization of text documents
- **Real-time Monitoring**: File watcher that automatically updates the vector database when documents are added, modified, or deleted
- **Vector Search**: Semantic similarity search using Qdrant vector database
- **LLM Integration**: Answer generation using Groq's Llama model
- **REST API**: FastAPI-based API for querying documents
- **Dockerized**: Complete Docker setup with docker-compose

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Documents     │───> │   Qdrant     │───> │   RAG Query     │
│  (.txt files)   │     │   Vector DB  │     │   Processing    │
└─────────────────┘     └──────────────┘     └─────────────────┘
         │                                           │
         ▼                                           ▼
┌─────────────────┐                          ┌─────────────────┐
│  File Watcher   │                          │  Groq LLM API   │
│   (Auto Sync)   │                          │  (Answer Gen)   │
└─────────────────┘                          └─────────────────┘
```

## Project Structure

```
RAG-QDRANT/
├── example_docs/           # Directory containing documents to be indexed
│   └── python_overview.txt # Sample document
├── .gitignore
├── docker-compose.yaml     # Docker services configuration
├── Dockerfile             # Container build instructions
├── ingest.py              # Document ingestion and vectorization
├── main.py                # FastAPI application entry point
├── rag.py                 # RAG logic and Groq integration
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script
└── watcher.py            # File system monitoring
```

## Prerequisites

- Docker and Docker Compose
- Groq API Key (get one from [Groq Console](https://console.groq.com/))

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/belgisanggita/rag-qdrant.git
cd RAG-QDRANT
```

### 2. Configure Environment

Edit the `docker-compose.yaml` file and replace `YOUR_API_KEY_HERE` with your actual Groq API key:

```yaml
environment:
  - GROQ_API_KEY=your_actual_groq_api_key_here
  - QDRANT_HOST=qdrant
  - QDRANT_PORT=6333
```

### 3. Add Your Documents

Place your `.txt` documents in the `example_docs/` directory:

```bash
cp your_document.txt example_docs/
```

### 4. Start the Services

```bash
docker-compose up --build
```

This will:
- Start Qdrant vector database on port 6333
- Build and start the RAG application on port 8000
- Automatically ingest documents from `example_docs/`
- Start the file watcher for real-time updates

### 5. Query Your Documents

Send a POST request to the API:

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Python used for?"}'
```

Example response:
```json
{
  "answer": "Python is used for web development, data analysis, artificial intelligence, and automation...",
  "context_used": "Python is a versatile programming language..."
}
```

## API Documentation

### Endpoints

#### POST `/ask`

Query the document database with a question.

**Request Body:**
```json
{
  "question": "Your question here"
}
```

**Response:**
```json
{
  "answer": "Generated answer based on context",
  "context_used": "Relevant document excerpts used for answer generation"
}
```
### API Usage Example

Here's an example of using the API with Postman: *Example POST request to `/ask` endpoint*

<img width="1919" height="1018" alt="Image" src="https://github.com/user-attachments/assets/eeab103e-b415-4cba-b7e9-ff00f3b74074" />

*Sample response showing generated answer and context used*

### Interactive API Docs

Once the service is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Components

### Document Ingestion (`ingest.py`)

- **Embedding Model**: Uses `sentence-transformers/all-MiniLM-L6-v2` for text vectorization
- **Vector Database**: Stores embeddings in Qdrant with 384-dimensional vectors
- **Smart Sync**: Only processes new or changed documents
- **Cleanup**: Automatically removes vectors for deleted documents

### RAG Pipeline (`rag.py`)

- **Semantic Search**: Finds top-k most similar documents using cosine similarity
- **Context Building**: Combines relevant documents for LLM context
- **Answer Generation**: Uses Groq's Llama-3.3-70B model with context-aware prompting
- **Accuracy Control**: LLM instructed to only use provided context, not external knowledge

### File Monitoring (`watcher.py`)

- **Real-time Updates**: Monitors `example_docs/` for file changes
- **Event Handling**: Responds to file creation, modification, and deletion
- **Automatic Sync**: Triggers document re-ingestion on changes

### Web API (`main.py`)

- **FastAPI Framework**: High-performance async web framework
- **Background Processing**: File watcher runs as daemon thread
- **Request Validation**: Pydantic models for request/response validation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `QDRANT_HOST` | Qdrant database host | `qdrant` |
| `QDRANT_PORT` | Qdrant database port | `6333` |


## Development

### Local Development Setup

For development without Docker:

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Start Qdrant**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

3. **Set Environment Variables**
```bash
export GROQ_API_KEY=your_api_key
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

4. **Run Components**
```bash
# Ingest documents
python ingest.py

# Start API server
uvicorn main:app --reload
```

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag
docker-compose logs -f qdrant
```

### Qdrant Web UI

Access Qdrant's web interface at `http://localhost:6333/dashboard`

## Troubleshooting

### Common Issues

1. **Groq API Key Error**
   - Ensure your API key is correctly set in docker-compose.yaml
   - Check Groq API quotas and limits

2. **Document Not Found**
   - Verify documents are in the `example_docs/` directory
   - Check file permissions and encoding (UTF-8 recommended)

3. **Connection Refused**
   - Ensure Qdrant container is running: `docker-compose ps`
   - Check network connectivity between containers

4. **Empty Responses**
   - Verify documents were successfully ingested
   - Check Qdrant dashboard for indexed points
   - Try more specific questions related to your document content

### Reset Database

To start fresh:

```bash
docker-compose down -v  # Remove volumes
docker-compose up --build
```

## Performance Considerations

- **Embedding Model**: all-MiniLM-L6-v2 provides good balance of speed vs accuracy
- **Vector Dimensions**: 384D vectors offer efficient storage and fast search
- **Batch Processing**: Large document sets should be processed in batches
- **Memory Usage**: Monitor Qdrant memory usage for large collections