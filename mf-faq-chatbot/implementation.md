# Implementation Plan
## MF FAQ Assistant — RAG Chatbot

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Date** | 2026-09-27 |
| **Based on** | PRD v1.0, Architecture v1.0 |
| **Estimated Total Time** | 4–6 hours |

---

## How to Use This Document

This implementation plan is designed for **phase-wise execution with Cursor**. Each phase:
- Has a clear objective
- Lists specific files to create/modify
- Includes verification steps
- Can be handed to Cursor as a self-contained prompt

**Cursor Prompt Template**:
```
Read architecture.md and implementation.md.
Implement Phase {N}: {Phase Name}.
Files to create: {file list}
Acceptance criteria: {criteria}
```

---

## Phase 0: Project Setup & Dependencies

### Objective
Initialize the Python project, install dependencies, and create the directory structure.

### Tasks
1. Create project directory structure
2. Create `requirements.txt` with all dependencies
3. Install dependencies
4. Verify installation

### Files to Create
- `requirements.txt`
- `src/__init__.py`

### `requirements.txt`
```txt
flask>=3.0.0
sentence-transformers>=2.2.0
chromadb>=0.4.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

### Verification
```bash
cd mf-faq-chatbot
pip install -r requirements.txt
python -c "import flask, sentence_transformers, chromadb; print('OK')"
```

### Acceptance Criteria
- [ ] All packages install without errors
- [ ] `python -c "import flask"` succeeds
- [ ] Directory structure matches architecture

---

## Phase 1: Data Ingestion — Structured Facts

### Objective
Create a structured JSON file containing all facts extracted from the 5 Groww scheme pages. This is the **single source of truth** for the RAG corpus.

### Tasks
1. Create `data/structured_facts.json` with all scheme facts
2. Create `src/config.py` with configuration constants
3. Create `src/loader.py` to load and validate the structured data

### Files to Create
- `data/structured_facts.json`
- `src/config.py`
- `src/loader.py`

### Data Schema (structured_facts.json)
```json
{
  "schemes": [
    {
      "name": "HDFC Large Cap Fund Direct Growth",
      "slug": "hdfc-large-cap-fund-direct-growth",
      "category": "Equity - Large Cap",
      "risk_level": "Very High",
      "expense_ratio": "1.03%",
      "min_sip": "₹100",
      "min_lumpsum": "₹100",
      "exit_load": "1% if redeemed within 1 year",
      "benchmark": "NIFTY 100 Total Return Index",
      "fund_managers": [
        {"name": "Rahul Baijal", "since": "Jul 2022"},
        {"name": "Dhruv Muchhal", "since": "Jun 2023"}
      ],
      "aum": "₹39,933.37 Cr",
      "nav": "₹1,189.08",
      "nav_date": "25 Sep 2026",
      "launch_date": "10 Dec 1999",
      "investment_objective": "The scheme seeks to provide long-term capital appreciation/income by investing predominantly in Large-Cap companies.",
      "stamp_duty": "0.005% (from July 1st, 2020)",
      "tax_implication": "If you redeem within one year, returns are taxed at 20%. If you redeem after one year, returns exceeding Rs 1.25 lakh in a financial year are taxed at 12.5%.",
      "lock_in": null,
      "source_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
    }
  ],
  "amc": {
    "name": "HDFC Mutual Fund",
    "rank": "#2 in India",
    "total_aum": "₹9,86,236.84 Cr",
    "website": "https://www.hdfcfund.com"
  }
}
```

### `src/config.py`
```python
"""Configuration constants for MF FAQ Assistant."""

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
TOP_K = 3
SCORE_THRESHOLD = 0.3

# Flask
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

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
```

### `src/loader.py`
```python
"""Load and validate structured facts from JSON."""
import json
from pathlib import Path
from typing import Dict, List, Any

def load_structured_facts(data_dir: Path) -> Dict[str, Any]:
    """Load structured facts from JSON file."""
    facts_path = data_dir / "structured_facts.json"
    if not facts_path.exists():
        raise FileNotFoundError(f"Structured facts not found: {facts_path}")
    with open(facts_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_scheme_by_slug(facts: Dict, slug: str) -> Dict:
    """Get a scheme by its slug."""
    for scheme in facts["schemes"]:
        if scheme["slug"] == slug:
            return scheme
    return None

def get_all_slugs(facts: Dict) -> List[str]:
    """Get all scheme slugs."""
    return [s["slug"] for s in facts["schemes"]]
```

### Verification
```bash
python -c "from src.loader import load_structured_facts; from src.config import DATA_DIR; facts = load_structured_facts(DATA_DIR); print(f'Loaded {len(facts[\"schemes\"])} schemes')"
```

### Acceptance Criteria
- [ ] `structured_facts.json` contains all 5 schemes
- [ ] Each scheme has all required fields
- [ ] `loader.py` loads and validates without errors
- [ ] All source URLs are valid

---

## Phase 2: Chunking Strategy

### Objective
Implement fact-based semantic chunking. Each chunk is one atomic fact about one scheme, with metadata for retrieval and citation.

### Tasks
1. Create `src/chunker.py` with chunking logic
2. Generate chunks from structured facts
3. Save chunks to `data/chunks.json`

### Files to Create
- `src/chunker.py`
- `data/chunks.json` (generated)

### `src/chunker.py`
```python
"""Fact-based semantic chunking for MF FAQ."""
from typing import Dict, List, Any

def chunk_scheme_facts(facts: Dict) -> List[Dict[str, Any]]:
    """
    Convert structured facts into atomic chunks.
    Each chunk = one fact about one scheme.
    """
    chunks = []
    chunk_id = 0

    for scheme in facts["schemes"]:
        slug = scheme["slug"]
        name = scheme["name"]
        source_url = scheme["source_url"]

        # Expense ratio
        chunks.append(_make_chunk(
            id=f"{slug}_expense_ratio",
            scheme=name, slug=slug, category="expense_ratio",
            text=f"The expense ratio of {name} is {scheme['expense_ratio']}.",
            value=scheme["expense_ratio"],
            source_url=source_url
        ))

        # Exit load
        chunks.append(_make_chunk(
            id=f"{slug}_exit_load",
            scheme=name, slug=slug, category="exit_load",
            text=f"Exit load of {name}: {scheme['exit_load']}.",
            value=scheme["exit_load"],
            source_url=source_url
        ))

        # Min SIP
        chunks.append(_make_chunk(
            id=f"{slug}_min_sip",
            scheme=name, slug=slug, category="min_sip",
            text=f"The minimum SIP investment for {name} is {scheme['min_sip']}.",
            value=scheme["min_sip"],
            source_url=source_url
        ))

        # Min lumpsum
        chunks.append(_make_chunk(
            id=f"{slug}_min_lumpsum",
            scheme=name, slug=slug, category="min_lumpsum",
            text=f"The minimum lumpsum investment for {name} is {scheme['min_lumpsum']}.",
            value=scheme["min_lumpsum"],
            source_url=source_url
        ))

        # Benchmark
        chunks.append(_make_chunk(
            id=f"{slug}_benchmark",
            scheme=name, slug=slug, category="benchmark",
            text=f"The benchmark of {name} is {scheme['benchmark']}.",
            value=scheme["benchmark"],
            source_url=source_url
        ))

        # Risk level
        chunks.append(_make_chunk(
            id=f"{slug}_risk_level",
            scheme=name, slug=slug, category="risk_level",
            text=f"{name} is rated {scheme['risk_level']} risk.",
            value=scheme["risk_level"],
            source_url=source_url
        ))

        # Fund managers
        managers = ", ".join([m["name"] for m in scheme["fund_managers"]])
        chunks.append(_make_chunk(
            id=f"{slug}_fund_manager",
            scheme=name, slug=slug, category="fund_manager",
            text=f"{name} is managed by {managers}.",
            value=managers,
            source_url=source_url
        ))

        # AUM
        chunks.append(_make_chunk(
            id=f"{slug}_aum",
            scheme=name, slug=slug, category="aum",
            text=f"The AUM of {name} is {scheme['aum']}.",
            value=scheme["aum"],
            source_url=source_url
        ))

        # Investment objective
        chunks.append(_make_chunk(
            id=f"{slug}_objective",
            scheme=name, slug=slug, category="investment_objective",
            text=f"{name} seeks to {scheme['investment_objective']}",
            value=scheme["investment_objective"],
            source_url=source_url
        ))

        # Lock-in (ELSS only)
        if scheme.get("lock_in"):
            chunks.append(_make_chunk(
                id=f"{slug}_lock_in",
                scheme=name, slug=slug, category="lock_in",
                text=f"{name} has a {scheme['lock_in']} lock-in period.",
                value=scheme["lock_in"],
                source_url=source_url
            ))

        # Tax
        chunks.append(_make_chunk(
            id=f"{slug}_tax",
            scheme=name, slug=slug, category="tax",
            text=f"Tax implication for {name}: {scheme['tax_implication']}",
            value=scheme["tax_implication"],
            source_url=source_url
        ))

        # Stamp duty
        chunks.append(_make_chunk(
            id=f"{slug}_stamp_duty",
            scheme=name, slug=slug, category="stamp_duty",
            text=f"Stamp duty on investment for {name}: {scheme['stamp_duty']}.",
            value=scheme["stamp_duty"],
            source_url=source_url
        ))

    return chunks


def _make_chunk(id, scheme, slug, category, text, value, source_url):
    return {
        "id": id,
        "scheme": scheme,
        "slug": slug,
        "category": category,
        "text": text,
        "value": value,
        "source_url": source_url,
        "metadata": {
            "amc": "HDFC Mutual Fund",
            "scheme_name": scheme,
            "category_type": category,
        }
    }
```

### Verification
```bash
python -c "
from src.loader import load_structured_facts
from src.chunker import chunk_scheme_facts
from src.config import DATA_DIR
facts = load_structured_facts(DATA_DIR)
chunks = chunk_scheme_facts(facts)
print(f'Generated {len(chunks)} chunks')
for c in chunks[:3]:
    print(f'  {c[\"id\"]}: {c[\"text\"][:60]}...')
"
```

### Acceptance Criteria
- [ ] Chunks generated for all 5 schemes
- [ ] Each scheme has 10–12 chunks (depending on lock_in)
- [ ] Total chunks ~50–60
- [ ] Each chunk has id, text, value, source_url, metadata

---

## Phase 3: Embedding & Vector Store

### Objective
Embed all chunks using `sentence-transformers/all-MiniLM-L6-v2` and store them in ChromaDB for similarity search.

### Tasks
1. Create `src/embedder.py` for embedding generation
2. Create `src/vector_store.py` for ChromaDB operations
3. Create `build_index.py` script to build the vector store
4. Run the build script

### Files to Create
- `src/embedder.py`
- `src/vector_store.py`
- `build_index.py`

### `src/embedder.py`
```python
"""Generate embeddings using sentence-transformers."""
from sentence_transformers import SentenceTransformer
from typing import List
from src.config import EMBEDDING_MODEL

_model = None

def get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into vectors."""
    model = get_model()
    return model.encode(texts, show_progress_bar=False).tolist()

def embed_query(query: str) -> List[float]:
    """Embed a single query."""
    return embed_texts([query])[0]
```

### `src/vector_store.py`
```python
"""ChromaDB vector store operations."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from src.config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR

_client = None
_collection = None

def get_client():
    """Get or create ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client

def get_collection():
    """Get or create the collection."""
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_chunks(chunks: List[Dict[str, Any]]):
    """Add chunks to the vector store."""
    collection = get_collection()

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Embed texts
    from src.embedder import embed_texts
    embeddings = embed_texts(texts)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def search(query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar chunks."""
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            chunks.append({
                "id": chunk_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine similarity
            })
    return chunks

def count_chunks() -> int:
    """Get the number of chunks in the store."""
    collection = get_collection()
    return collection.count()

def clear_collection():
    """Delete and recreate the collection."""
    global _collection
    client = get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    _collection = None
```

### `build_index.py`
```python
#!/usr/bin/env python3
"""Build the vector store index from structured facts."""
from src.loader import load_structured_facts
from src.chunker import chunk_scheme_facts
from src.vector_store import add_chunks, clear_collection, count_chunks
from src.config import DATA_DIR

def main():
    print("Loading structured facts...")
    facts = load_structured_facts(DATA_DIR)
    print(f"  Loaded {len(facts['schemes'])} schemes")

    print("Generating chunks...")
    chunks = chunk_scheme_facts(facts)
    print(f"  Generated {len(chunks)} chunks")

    print("Clearing existing collection...")
    clear_collection()

    print("Embedding and storing chunks...")
    add_chunks(chunks)
    print(f"  Stored {count_chunks()} chunks in ChromaDB")

    print("Build complete!")

if __name__ == "__main__":
    main()
```

### Verification
```bash
python build_index.py
# Expected output:
# Loading structured facts...
#   Loaded 5 schemes
# Generating chunks...
#   Generated 55 chunks
# Clearing existing collection...
# Embedding and storing chunks...
#   Stored 55 chunks in ChromaDB
# Build complete!
```

### Acceptance Criteria
- [ ] `build_index.py` runs without errors
- [ ] ChromaDB collection created with ~55 chunks
- [ ] `count_chunks()` returns correct number
- [ ] Embedding model loads successfully

---

## Phase 4: Query Classification

### Objective
Implement a query classifier that routes queries to the correct handler (factual, advice, performance, greeting, unknown).

### Tasks
1. Create `src/classifier.py` with classification logic
2. Test with sample queries

### Files to Create
- `src/classifier.py`

### `src/classifier.py`
```python
"""Query classification for MF FAQ Assistant."""
import re
from typing import Dict, Any

# Patterns for advice/opinion queries
ADVICE_PATTERNS = [
    r"should i (buy|sell|invest|put)",
    r"is .+ good (to|for) (buy|invest)",
    r"best (fund|scheme|mutual)",
    r"recommend",
    r"which fund (should|to)",
    r"portfolio",
    r"how much should i invest",
    r"worth (buying|investing)",
    r"good investment",
    r"should i (start|stop)",
]

# Patterns for performance queries
PERFORMANCE_PATTERNS = [
    r"return",
    r"performance",
    r"profit",
    r"gain",
    r"yield",
    r"how much (will|would|can) i (make|earn|get)",
    r"growth",
]

# Patterns for greetings
GREETING_PATTERNS = [
    r"^(hi|hello|hey|namaste|good (morning|afternoon|evening))",
    r"^help$",
    r"^what can you do",
]

# Patterns for factual queries
FACTUAL_PATTERNS = [
    r"expense ratio",
    r"exit load",
    r"minimum (sip|lumpsum|investment)",
    r"benchmark",
    r"risk",
    r"fund manager",
    r"aum",
    r"nav",
    r"lock.?in",
    r"tax",
    r"stamp duty",
    r"objective",
    r"category",
    r"launch date",
    r"holdings",
]


def classify_query(query: str) -> Dict[str, Any]:
    """
    Classify a user query into a type.
    Returns: {"type": str, "confidence": float}
    """
    query_lower = query.lower().strip()

    # Check advice patterns
    for pattern in ADVICE_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "advice", "confidence": 1.0}

    # Check performance patterns
    for pattern in PERFORMANCE_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "performance", "confidence": 1.0}

    # Check greeting patterns
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "greeting", "confidence": 1.0}

    # Check factual patterns
    for pattern in FACTUAL_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "factual", "confidence": 0.9}

    # Default: try factual retrieval (might still find relevant chunks)
    return {"type": "factual", "confidence": 0.5}
```

### Verification
```bash
python -c "
from src.classifier import classify_query
tests = [
    'Expense ratio of HDFC Large Cap?',
    'Should I buy HDFC Small Cap?',
    'What are the returns of HDFC ELSS?',
    'Hello!',
    'Minimum SIP for HDFC Flexi Cap?',
]
for q in tests:
    r = classify_query(q)
    print(f'{q:45s} -> {r[\"type\"]:12s} ({r[\"confidence\"]})')
"
```

### Acceptance Criteria
- [ ] Factual queries classified as "factual"
- [ ] Advice queries classified as "advice"
- [ ] Performance queries classified as "performance"
- [ ] Greetings classified as "greeting"
- [ ] Unknown queries default to "factual" with low confidence

---

## Phase 5: Retrieval & Answer Generation

### Objective
Implement the retrieval module (ChromaDB similarity search) and the template-based answer generator.

### Tasks
1. Create `src/retriever.py` for similarity search
2. Create `src/generator.py` for answer generation
3. Create `src/pipeline.py` to tie everything together

### Files to Create
- `src/retriever.py`
- `src/generator.py`
- `src/pipeline.py`

### `src/retriever.py`
```python
"""Retrieval module for MF FAQ."""
from typing import List, Dict, Any
from src.embedder import embed_query
from src.vector_store import search
from src.config import TOP_K, SCORE_THRESHOLD

def retrieve(query: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks for a query.
    Returns filtered and ranked chunks.
    """
    # Embed the query
    query_embedding = embed_query(query)

    # Search ChromaDB
    results = search(query_embedding, top_k=TOP_K)

    # Filter by score threshold
    filtered = [r for r in results if r["score"] >= SCORE_THRESHOLD]

    return filtered
```

### `src/generator.py`
```python
"""Template-based answer generation for MF FAQ."""
from typing import Dict, Any, Optional

# Educational links
AMFI_URL = "https://www.amfiindia.com"
SEBI_URL = "https://www.sebi.gov.in"
HDFC_FUND_URL = "https://www.hdfcfund.com"

# Refusal messages
ADVICE_REFUSAL = (
    "I can only provide factual information about mutual fund schemes — "
    "I can't give investment advice or recommendations. "
    "For guidance on whether a scheme fits your goals, please consult a "
    "certified financial planner. You can learn more about mutual fund "
    "basics here: {link}"
)

PERFORMANCE_REFUSAL = (
    "I can't compute or compare returns. Please refer to the official "
    "factsheet for performance data: {link}"
)

def generate_answer(query_type: str, chunks: list, query: str = "") -> Dict[str, Any]:
    """
    Generate an answer based on query type and retrieved chunks.
    """
    if query_type == "advice":
        return {
            "type": "refusal",
            "answer": ADVICE_REFUSAL.format(link=AMFI_URL),
            "source": AMFI_URL,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "performance":
        # Use the first chunk's source or default to HDFC fund site
        link = chunks[0]["metadata"].get("source_url", HDFC_FUND_URL) if chunks else HDFC_FUND_URL
        return {
            "type": "performance",
            "answer": PERFORMANCE_REFUSAL.format(link=link),
            "source": link,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "greeting":
        return {
            "type": "greeting",
            "answer": (
                "Hello! I'm the MF FAQ Assistant. I can answer factual questions "
                "about HDFC mutual fund schemes — expense ratio, exit load, "
                "minimum SIP, benchmark, risk level, and more. "
                "Facts-only. No investment advice."
            ),
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    # Factual query
    if not chunks:
        return {
            "type": "not_found",
            "answer": (
                "I couldn't find specific information about that. "
                "Try asking about expense ratio, exit load, minimum SIP, "
                "benchmark, risk level, fund manager, or lock-in period."
            ),
            "source": None,
            "scheme": None,
            "confidence": 0.0,
        }

    # Use the best chunk
    best = chunks[0]
    answer_text = best["text"]
    source_url = best["metadata"].get("source_url", "")
    scheme_name = best["metadata"].get("scheme_name", "")

    return {
        "type": "factual",
        "answer": answer_text,
        "source": source_url,
        "scheme": scheme_name,
        "confidence": best.get("score", 0.0),
    }
```

### `src/pipeline.py`
```python
"""End-to-end RAG pipeline."""
from typing import Dict, Any
from src.classifier import classify_query
from src.retriever import retrieve
from src.generator import generate_answer

def process_query(query: str) -> Dict[str, Any]:
    """
    Process a user query through the full RAG pipeline:
    Classify → Retrieve → Generate
    """
    # Step 1: Classify
    classification = classify_query(query)
    query_type = classification["type"]

    # Step 2: Retrieve (only for factual queries)
    chunks = []
    if query_type == "factual":
        chunks = retrieve(query)

    # Step 3: Generate
    result = generate_answer(query_type, chunks, query)

    # Add classification info
    result["query_type"] = query_type
    result["retrieved_chunks"] = len(chunks)

    return result
```

### Verification
```bash
python -c "
from src.pipeline import process_query
queries = [
    'Expense ratio of HDFC Large Cap Fund?',
    'ELSS lock-in period?',
    'Minimum SIP for HDFC Small Cap?',
    'Should I buy HDFC Flexi Cap?',
    'What are the returns of HDFC ELSS?',
]
for q in queries:
    r = process_query(q)
    print(f'Q: {q}')
    print(f'  Type: {r[\"type\"]}')
    print(f'  Answer: {r[\"answer\"][:80]}...')
    print(f'  Source: {r[\"source\"]}')
    print()
"
```

### Acceptance Criteria
- [ ] Factual queries return answers with citations
- [ ] Advice queries return refusal with AMFI link
- [ ] Performance queries return factsheet link
- [ ] Greetings return welcome message
- [ ] Unknown queries return clarification prompt
- [ ] All answers ≤ 3 sentences

---

## Phase 6: Flask Web Application

### Objective
Create the Flask web app with a simple chat UI.

### Tasks
1. Create `app.py` with Flask routes
2. Create `templates/index.html` with chat UI
3. Create `static/style.css` for styling
4. Create `static/app.js` for frontend logic
5. Test the app

### Files to Create
- `app.py`
- `templates/index.html`
- `static/style.css`
- `static/app.js`

### `app.py`
```python
"""Flask web application for MF FAQ Assistant."""
from flask import Flask, render_template, request, jsonify
from src.pipeline import process_query
from src.vector_store import count_chunks
from src.config import SOURCE_URLS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)

@app.route("/")
def index():
    """Render the chat UI."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Process a chat message."""
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "type": "error",
            "answer": "Please enter a question.",
            "source": None,
        })

    result = process_query(query)
    return jsonify(result)

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "chunks_loaded": count_chunks(),
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_db": "chroma",
    })

@app.route("/sources")
def sources():
    """List source URLs."""
    return jsonify({"sources": SOURCE_URLS})

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
```

### `templates/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MF FAQ Assistant</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>MF FAQ Assistant</h1>
            <p class="disclaimer">Facts-only. No investment advice.</p>
        </header>

        <div class="welcome">
            <p>Welcome! Ask me about HDFC mutual fund schemes.</p>
            <div class="examples">
                <p>Try asking:</p>
                <button class="example-btn" onclick="askExample(this)">
                    Expense ratio of HDFC Large Cap Fund?
                </button>
                <button class="example-btn" onclick="askExample(this)">
                    ELSS lock-in period?
                </button>
                <button class="example-btn" onclick="askExample(this)">
                    Minimum SIP for HDFC Small Cap?
                </button>
            </div>
        </div>

        <div id="chat" class="chat"></div>

        <form id="chat-form" class="chat-form">
            <input type="text" id="query" placeholder="Type your question..." autocomplete="off">
            <button type="submit">Send</button>
        </form>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>
```

### `static/style.css`
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
}
.container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
}
header {
    text-align: center;
    margin-bottom: 20px;
}
header h1 { color: #1a73e8; }
.disclaimer {
    color: #e8710a;
    font-weight: 600;
    margin-top: 5px;
}
.welcome {
    background: #e8f0fe;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}
.examples { margin-top: 10px; }
.example-btn {
    display: block;
    width: 100%;
    padding: 8px 12px;
    margin: 5px 0;
    background: #fff;
    border: 1px solid #dadce0;
    border-radius: 4px;
    cursor: pointer;
    text-align: left;
    font-size: 14px;
}
.example-btn:hover { background: #f1f3f4; }
.chat {
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 15px;
}
.message {
    margin: 10px 0;
    padding: 10px 15px;
    border-radius: 8px;
    max-width: 80%;
}
.message.user {
    background: #1a73e8;
    color: #fff;
    margin-left: auto;
}
.message.bot {
    background: #fff;
    border: 1px solid #dadce0;
}
.message .source {
    display: block;
    margin-top: 8px;
    font-size: 12px;
    color: #1a73e8;
}
.message .source a { color: #1a73e8; }
.message.refusal {
    background: #fef7e0;
    border-color: #f9ab00;
}
.chat-form {
    display: flex;
    gap: 10px;
}
.chat-form input {
    flex: 1;
    padding: 12px;
    border: 1px solid #dadce0;
    border-radius: 4px;
    font-size: 16px;
}
.chat-form button {
    padding: 12px 24px;
    background: #1a73e8;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}
.chat-form button:hover { background: #1557b0; }
```

### `static/app.js`
```javascript
const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const input = document.getElementById('query');

function addMessage(text, isUser = false, source = null, type = '') {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user' : 'bot'} ${type}`;
    div.textContent = text;

    if (source) {
        const sourceDiv = document.createElement('span');
        sourceDiv.className = 'source';
        sourceDiv.innerHTML = `Source: <a href="${source}" target="_blank">${source}</a>`;
        div.appendChild(sourceDiv);
    }

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function askExample(btn) {
    input.value = btn.textContent;
    form.dispatchEvent(new Event('submit'));
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    addMessage(query, true);
    input.value = '';

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        const data = await res.json();
        addMessage(data.answer, false, data.source, data.type === 'refusal' ? 'refusal' : '');
    } catch (err) {
        addMessage('Sorry, something went wrong. Please try again.');
    }
});
```

### Verification
```bash
python app.py
# Open http://127.0.0.1:5000 in browser
# Test: Type "Expense ratio of HDFC Large Cap Fund?" and verify response
```

### Acceptance Criteria
- [ ] Flask app starts on port 5000
- [ ] UI loads with welcome message and 3 example buttons
- [ ] Example buttons populate input and submit
- [ ] Chat messages appear with user/bot styling
- [ ] Citation links are clickable
- [ ] Refusal messages appear in amber/yellow
- [ ] Disclaimer visible in header

---

## Phase 7: Source List, Sample Q&A, README

### Objective
Create the remaining deliverables: source list, sample Q&A file, and README.

### Tasks
1. Create `sources.csv`
2. Create `sample_qa.md` with 10 Q&A pairs
3. Create `README.md` with setup instructions

### Files to Create
- `sources.csv`
- `sample_qa.md`
- `README.md`

### `sources.csv`
```csv
scheme_name,category,url
HDFC Large Cap Fund Direct Growth,Equity - Large Cap,https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
HDFC Flexi Cap Direct Plan Growth,Equity - Flexi Cap,https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
HDFC ELSS Tax Saver Fund Direct Plan Growth,Equity - ELSS,https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
HDFC Small Cap Fund Direct Growth,Equity - Small Cap,https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
HDFC Balanced Advantage Fund Direct Growth,Hybrid - Dynamic Asset Allocation,https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth
```

### `sample_qa.md`
```markdown
# Sample Q&A — MF FAQ Assistant

## Q1: What is the expense ratio of HDFC Large Cap Fund?
**A:** The expense ratio of HDFC Large Cap Fund Direct Growth is 1.03%.
**Source:** https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth

## Q2: What is the lock-in period for HDFC ELSS Tax Saver Fund?
**A:** HDFC ELSS Tax Saver Fund Direct Plan Growth has a 3-year lock-in period from the date of investment.
**Source:** https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth

## Q3: What is the minimum SIP for HDFC Small Cap Fund?
**A:** The minimum SIP investment for HDFC Small Cap Fund Direct Growth is ₹100.
**Source:** https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth

## Q4: What is the exit load of HDFC Flexi Cap Fund?
**A:** Exit load of HDFC Flexi Cap Direct Plan Growth: 1% if redeemed within 1 year.
**Source:** https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth

## Q5: What is the benchmark of HDFC Balanced Advantage Fund?
**A:** The benchmark of HDFC Balanced Advantage Fund Direct Growth is NIFTY 50 Hybrid Composite Debt 50:50 Index.
**Source:** https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth

## Q6: Who manages HDFC Large Cap Fund?
**A:** HDFC Large Cap Fund Direct Growth is managed by Rahul Baijal (since Jul 2022) and Dhruv Muchhal (since Jun 2023).
**Source:** https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth

## Q7: What is the risk level of HDFC Small Cap Fund?
**A:** HDFC Small Cap Fund Direct Growth is rated Very High risk.
**Source:** https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth

## Q8: Should I buy HDFC Flexi Cap Fund?
**A:** I can only provide factual information about mutual fund schemes — I can't give investment advice or recommendations. For guidance on whether a scheme fits your goals, please consult a certified financial planner. You can learn more about mutual fund basics here: https://www.amfiindia.com
**Source:** https://www.amfiindia.com

## Q9: What are the returns of HDFC ELSS Tax Saver Fund?
**A:** I can't compute or compare returns. Please refer to the official factsheet for performance data: https://www.hdfcfund.com
**Source:** https://www.hdfcfund.com

## Q10: What is the minimum lumpsum investment for HDFC ELSS Tax Saver Fund?
**A:** The minimum lumpsum investment for HDFC ELSS Tax Saver Fund Direct Plan Growth is ₹500.
**Source:** https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
```

### `README.md`
```markdown
# MF FAQ Assistant — RAG Chatbot

A facts-only FAQ assistant for HDFC Mutual Fund schemes, built with RAG (Retrieval-Augmented Generation).

## Features
- Answers factual questions about 5 HDFC mutual fund schemes
- Every answer includes a source citation link
- Refuses investment advice with educational links
- Full RAG pipeline: Loading → Chunking → Embedding → Vector Store → Retrieval → Generation
- Tiny web UI with welcome message and example questions

## Tech Stack
- **Python 3.10+**
- **Flask** — web framework
- **sentence-transformers/all-MiniLM-L6-v2** — embedding model
- **ChromaDB** — vector database
- **BeautifulSoup4** — HTML parsing (for ingestion)

## Quick Start

### 1. Install Dependencies
```bash
cd mf-faq-chatbot
pip install -r requirements.txt
```

### 2. Build the Vector Index
```bash
python build_index.py
```

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
```
http://127.0.0.1:5000
```

## Project Structure
```
mf-faq-chatbot/
├── app.py                  # Flask web app
├── build_index.py          # Build vector index
├── requirements.txt        # Dependencies
├── sources.csv             # Source URLs
├── sample_qa.md            # Sample Q&A
├── data/
│   └── structured_facts.json
├── src/
│   ├── config.py
│   ├── loader.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   ├── classifier.py
│   ├── retriever.py
│   ├── generator.py
│   └── pipeline.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── vector_db/              # ChromaDB storage
```

## Scope
- **AMC**: HDFC Mutual Fund
- **Schemes**: Large Cap, Flexi Cap, ELSS, Small Cap, Balanced Advantage

## Known Limitations
- Static corpus (fetched once at build time)
- Single AMC (HDFC only)
- Template-based generation (no free-form LLM)
- No conversation memory (stateless)
- English only

## Disclaimer
**Facts-only. No investment advice.** This tool provides factual information from public sources only. It does not provide investment advice, recommendations, or portfolio guidance. Always consult a certified financial planner before making investment decisions.
```

### Acceptance Criteria
- [ ] `sources.csv` has all 5 URLs
- [ ] `sample_qa.md` has 10 Q&A pairs with answers and links
- [ ] `README.md` has clear setup steps
- [ ] Fresh setup works in < 10 minutes

---

## Phase 8: Integration Testing & Polish

### Objective
End-to-end testing, edge case handling, and final polish.

### Tasks
1. Test all sample Q&A pairs through the API
2. Test edge cases (empty query, PII input, unknown scheme)
3. Add error handling improvements
4. Final UI polish

### Test Script
```bash
python -c "
import requests
import json

BASE = 'http://127.0.0.1:5000'

# Health check
r = requests.get(f'{BASE}/health')
print('Health:', r.json())

# Test queries
queries = [
    'Expense ratio of HDFC Large Cap Fund?',
    'ELSS lock-in period?',
    'Minimum SIP for HDFC Small Cap?',
    'Should I buy HDFC Flexi Cap?',
    'What are the returns of HDFC ELSS?',
    'Hello!',
    'Who manages HDFC Balanced Advantage?',
    'What is the benchmark of HDFC Small Cap?',
]

for q in queries:
    r = requests.post(f'{BASE}/chat', json={'query': q})
    data = r.json()
    print(f'Q: {q}')
    print(f'  Type: {data[\"type\"]}')
    print(f'  Answer: {data[\"answer\"][:80]}...')
    print(f'  Source: {data.get(\"source\", \"N/A\")}')
    print()
"
```

### Edge Cases to Handle
| Query | Expected Behavior |
|-------|-------------------|
| Empty string | "Please enter a question." |
| "My PAN is ABCDE1234F" | Strip PII, respond normally |
| "asdfghjkl" | "I couldn't find specific information..." |
| "HDFC Mid Cap Fund?" | "I couldn't find... Try asking about [available schemes]" |

### Acceptance Criteria
- [ ] All 10 sample Q&A pairs return correct answers
- [ ] Advice queries refused with AMFI link
- [ ] Performance queries return factsheet link
- [ ] Empty queries handled gracefully
- [ ] PII in queries is stripped (not stored)
- [ ] Response time < 3 seconds
- [ ] UI renders correctly on mobile width

---

## Summary: Phase Completion Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project Setup & Dependencies | [ ] |
| 1 | Data Ingestion — Structured Facts | [ ] |
| 2 | Chunking Strategy | [ ] |
| 3 | Embedding & Vector Store | [ ] |
| 4 | Query Classification | [ ] |
| 5 | Retrieval & Answer Generation | [ ] |
| 6 | Flask Web Application | [ ] |
| 7 | Source List, Sample Q&A, README | [ ] |
| 8 | Integration Testing & Polish | [ ] |

---

*End of Implementation Plan*
