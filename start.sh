#!/bin/bash

echo "Running document ingestion..."
python ingest.py

echo "Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload