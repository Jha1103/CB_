"""Configuration constants for MF FAQ Assistant."""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db"
RAW_PAGES_DIR = DATA_DIR / "raw_pages"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# ChromaDB
CHROMA_COLLECTION = "mf_faq_chunks"
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR)

# Retrieval
TOP_K = 5
SCORE_THRESHOLD = 0.15
RELEVANCE_THRESHOLD = 0.55

# Flask
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Memory optimization for Render free tier
os.environ.setdefault("TORCH_DEVICE", "cpu")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

# Source URLs
SOURCE_URLS = {
    "hdfc-large-cap-fund-direct-growth": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc-equity-fund-direct-growth": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "hdfc-elss-tax-saver-fund-direct-plan-growth": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "hdfc-small-cap-fund-direct-growth": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "hdfc-balanced-advantage-fund-direct-growth": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
}

# Educational links
AMFI_URL = "https://www.amfiindia.com"
SEBI_URL = "https://www.sebi.gov.in"
HDFC_FUND_URL = "https://www.hdfcfund.com"
