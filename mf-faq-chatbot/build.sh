#!/usr/bin/env bash
set -e

echo "Installing CPU-only torch (smaller memory footprint)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "Installing other dependencies..."
pip install -r requirements.txt

echo "Building vector index..."
python3 build_index.py

echo "Build complete!"
