#!/bin/bash

curl -X DELETE http://${QDRANT_HOST}:${QDRANT_PORT}/collections/docs
echo "Running document ingestion..."
python ingest.py

echo "Starting API server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload