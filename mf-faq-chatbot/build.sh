#!/usr/bin/env bash
set -e

echo "Installing CPU-only torch (smaller memory footprint)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "Installing other dependencies..."
pip install -r requirements.txt

echo "Pre-downloading embedding model (cached for faster startup)..."
python3 -c "
from sentence_transformers import SentenceTransformer
import os
os.environ['TORCH_DEVICE'] = 'cpu'
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('Model cached successfully!')
"

echo "Building vector index..."
python3 build_index.py

echo "Build complete!"
