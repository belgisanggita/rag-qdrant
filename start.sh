#!/bin/bash

curl -s -X DELETE http://${QDRANT_HOST}:${QDRANT_PORT}/collections/docs &> /dev/null
echo "Running document ingestion..."
python ingest.py

echo "Starting API server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload