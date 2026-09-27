# Architecture Document
## MF FAQ Assistant — RAG Chatbot

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Date** | 2026-09-27 |
| **Based on** | PRD v1.0 |

---

## 1. System Overview

The MF FAQ Assistant is a **Retrieval-Augmented Generation (RAG)** system that answers factual questions about mutual fund schemes. It follows a classic RAG pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    (Flask Web App)                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask)                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐     │
│  │ /chat POST  │  │ /health GET  │  │ /sources GET       │     │
│  └──────┬──────┘  └──────────────┘  └────────────────────┘     │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RAG ENGINE (Python)                            │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Query      │───▶│  Retrieval   │───▶│   Generation     │  │
│  │   Classifier │    │  (ChromaDB)  │    │   (Template)     │  │
│  └──────────────┘    └──────┬───────┘    └──────────────────┘  │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │  Embedding      │                          │
│                    │  (MiniLM-L6-v2) │                          │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                     │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  ChromaDB        │    │  Structured      │                   │
│  │  (Vector Store)  │    │  Facts (JSON)    │                   │
│  │  - embeddings    │    │  - scheme facts  │                   │
│  │  - metadata      │    │  - source URLs   │                   │
│  │  - source links  │    │  - chunk map     │                   │
│  └──────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. RAG Pipeline Architecture

### 2.1 Data Ingestion Pipeline (Offline / Build Time)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   LOAD      │────▶│   PARSE      │────▶│   CHUNK      │────▶│   EMBED      │
│             │     │              │     │              │     │              │
│ Groww pages │     │ Extract      │     │ Fact-based   │     │ MiniLM-L6-v2 │
│ (HTML/MD)   │     │ structured   │     │ semantic     │     │ 384-dim      │
│             │     │ facts        │     │ chunks       │     │ embeddings   │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                     │
                                                                     ▼
                                                              ┌──────────────┐
                                                              │    STORE     │
                                                              │              │
                                                              │ ChromaDB     │
                                                              │ (persistent) │
                                                              └──────────────┘
```

### 2.2 Retrieval Pipeline (Online / Query Time)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   USER      │────▶│   EMBED      │────▶│   SEARCH     │────▶│   RANK &     │
│   QUERY     │     │   QUERY      │     │   ChromaDB   │     │   FILTER     │
│             │     │              │     │              │     │              │
│ "Expense    │     │ MiniLM-L6-v2 │     │ cosine sim   │     │ top-k=3      │
│  ratio of   │     │ → 384-dim    │     │ threshold    │     │ score > 0.3  │
│  HDFC LC?"  │     │              │     │              │     │              │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                     │
                                                                     ▼
                                                              ┌──────────────┐
                                                              │   GENERATE   │
                                                              │              │
                                                              │ Template-    │
                                                              │ based answer │
                                                              │ + citation   │
                                                              └──────────────┘
```

---

## 3. Component Details

### 3.1 Data Loader
- **Input**: Raw HTML/Markdown from Groww scheme pages
- **Output**: Structured JSON with scheme facts
- **Responsibilities**:
  - Fetch pages via HTTP (or load from saved files)
  - Parse and extract key data points
  - Normalize field names
  - Attach source URL metadata

### 3.2 Chunking Strategy: Fact-Based Semantic Chunking

**Why not fixed-size chunking?**
- Fixed-size chunks split related facts across boundaries
- FAQ queries target specific facts, not arbitrary text windows
- Fact-based chunks are self-contained and directly answerable

**Strategy**: Each chunk = one atomic fact about one scheme.

```
Chunk Schema:
{
  "id": "hdfc_large_cap_expense_ratio",
  "scheme": "HDFC Large Cap Fund Direct Growth",
  "scheme_slug": "hdfc-large-cap-fund-direct-growth",
  "category": "expense_ratio",       // expense_ratio, exit_load, min_sip, etc.
  "text": "The expense ratio of HDFC Large Cap Fund Direct Growth is 1.03%.",
  "value": "1.03%",
  "source_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
  "metadata": {
    "amc": "HDFC Mutual Fund",
    "category_type": "Equity - Large Cap",
    "risk_level": "Very High"
  }
}
```

**Chunk Categories**:
| Category | Example |
|----------|---------|
| `expense_ratio` | "The expense ratio of X is Y%." |
| `exit_load` | "Exit load of X: 1% if redeemed within 1 year." |
| `min_sip` | "Minimum SIP for X is ₹Y." |
| `min_lumpsum` | "Minimum lumpsum for X is ₹Y." |
| `benchmark` | "The benchmark of X is Y." |
| `risk_level` | "X is rated Very High risk." |
| `fund_manager` | "X is managed by Y since Z." |
| `aum` | "The AUM of X is ₹Y Cr." |
| `nav` | "The NAV of X as of date is ₹Y." |
| `investment_objective` | "X seeks to Y." |
| `lock_in` | "X has a 3-year lock-in period." |
| `tax` | "If redeemed within 1 year, returns are taxed at 20%." |
| `stamp_duty` | "Stamp duty on investment: 0.005%." |

### 3.3 Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Why this model**:
  - Lightweight (80MB), runs on CPU
  - Good semantic similarity for short factual text
  - No API key required
  - Fast inference (< 10ms per text)
- **Embedding caching**: Pre-compute all chunk embeddings at build time

### 3.4 Vector Store: ChromaDB
- **Collection**: `mf_faq_chunks`
- **Distance metric**: Cosine similarity
- **Persistence**: Local directory (`./vector_db/`)
- **Metadata filtering**: By `scheme_slug`, `category`

**Collection Schema**:
```
Collection: mf_faq_chunks
├── ids: [chunk_id, ...]
├── embeddings: [[384-dim vector], ...]
├── documents: [chunk_text, ...]
├── metadatas: [{scheme, category, source_url, ...}, ...]
```

### 3.5 Retrieval Module
- **Input**: User query (string)
- **Process**:
  1. Classify query type (factual vs. advice vs. performance)
  2. If factual: embed query → ChromaDB similarity search → top-k=3
  3. Filter by score threshold (> 0.3)
  4. Return ranked chunks with metadata
- **Output**: List of relevant chunks with source URLs

### 3.6 Query Classifier
- **Purpose**: Route queries to correct handler
- **Types**:
  - `FACTUAL` → RAG retrieval + template answer
  - `ADVICE` → Refusal message + educational link
  - `PERFORMANCE` → Factsheet link
  - `GREETING` → Welcome message
  - `UNKNOWN` → Clarification prompt

**Classification Rules** (keyword/pattern matching):
```python
ADVICE_PATTERNS = [
    r"should i (buy|sell|invest)",
    r"is .* good (to|for) (buy|invest)",
    r"best (fund|scheme)",
    r"recommend",
    r"which fund (should|to)",
    r"portfolio",
    r"how much should i invest",
]

PERFORMANCE_PATTERNS = [
    r"return",
    r"performance",
    r"profit",
    r"gain",
    r"yield",
]
```

### 3.7 Answer Generator
- **Type**: Template-based (no LLM)
- **Why template-based?**:
  - Guarantees facts-only output (no hallucination)
  - Deterministic and debuggable
  - No API key dependency
  - Perfect for class demo
- **Templates**:
  - Expense ratio: "The expense ratio of {scheme} is {value}."
  - Exit load: "Exit load of {scheme}: {value}."
  - Min SIP: "The minimum SIP investment for {scheme} is {value}."
  - Benchmark: "The benchmark of {scheme} is {value}."
  - Risk level: "{scheme} is rated {value} risk."
  - Lock-in: "{scheme} has a {value} lock-in period."
  - Advice refusal: "I can only provide factual information... [educational link]"
  - Performance: "I can't compute returns. Please refer to the official factsheet: [link]"

### 3.8 Web UI (Flask)
- **Framework**: Flask (lightweight, no build step)
- **Template**: Single `index.html` with embedded CSS/JS
- **Endpoints**:
  - `GET /` → Render chat UI
  - `POST /chat` → Process query, return JSON response
  - `GET /health` → Health check
  - `GET /sources` → List source URLs

---

## 4. Data Flow

### 4.1 Build-Time Flow
```
1. Load raw pages (HTML/MD) from data/raw_pages/
2. Parse and extract structured facts → data/structured_facts.json
3. Chunk facts into atomic units → chunks list
4. Embed each chunk → 384-dim vectors
5. Store in ChromaDB → vector_db/
6. Save chunk-to-source mapping → data/chunk_index.json
```

### 4.2 Query-Time Flow
```
1. User types question in UI
2. Frontend sends POST /chat {query}
3. Query classifier determines type
4. If FACTUAL:
   a. Embed query → 384-dim vector
   b. ChromaDB cosine similarity search → top-3 chunks
   c. Filter by score threshold
   d. Select best chunk
   e. Generate template answer + citation
5. If ADVICE → return refusal + educational link
6. If PERFORMANCE → return factsheet link
7. Return JSON {answer, source, type}
8. Frontend renders answer with clickable citation
```

---

## 5. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.10+ |
| Web Framework | Flask | 3.0+ |
| Embedding Model | sentence-transformers | 2.2+ |
| Vector DB | ChromaDB | 0.4+ |
| HTML Parser | BeautifulSoup4 | 4.12+ |
| HTTP Client | requests | 2.31+ |
| Data Format | JSON | stdlib |
| Frontend | Vanilla HTML/CSS/JS | — |

---

## 6. Project Structure

```
mf-faq-chatbot/
├── PRD.md                          # Product requirements
├── architecture.md                 # This file
├── implementation.md               # Phase-wise implementation plan
├── README.md                       # Setup and usage
├── requirements.txt                # Python dependencies
├── app.py                          # Flask web application
├── run.py                          # Entry point (build + serve)
├── sources.csv                     # Source URL list
├── sample_qa.md                    # Sample Q&A pairs
├── data/
│   ├── raw_pages/                  # Saved raw HTML/MD
│   │   ├── hdfc_large_cap.md
│   │   ├── hdfc_flexi_cap.md
│   │   ├── hdfc_elss.md
│   │   ├── hdfc_small_cap.md
│   │   └── hdfc_balanced_advantage.md
│   ├── structured_facts.json       # Extracted structured data
│   └── chunk_index.json            # Chunk-to-source mapping
├── src/
│   ├── __init__.py
│   ├── config.py                   # Configuration constants
│   ├── loader.py                   # Data loading and parsing
│   ├── chunker.py                  # Fact-based chunking
│   ├── embedder.py                 # Embedding generation
│   ├── vector_store.py             # ChromaDB operations
│   ├── classifier.py               # Query classification
│   ├── retriever.py                # Similarity search
│   ├── generator.py                # Answer generation
│   └── pipeline.py                 # End-to-end RAG pipeline
├── templates/
│   └── index.html                  # Chat UI
├── static/
│   ├── style.css                   # Styles
│   └── app.js                      # Frontend logic
└── vector_db/                      # ChromaDB persistent storage
    └── chroma.sqlite3
```

---

## 7. API Design

### 7.1 POST /chat
**Request**:
```json
{
  "query": "Expense ratio of HDFC Large Cap Fund?"
}
```

**Response (Factual)**:
```json
{
  "type": "factual",
  "answer": "The expense ratio of HDFC Large Cap Fund Direct Growth is 1.03%.",
  "source": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
  "scheme": "HDFC Large Cap Fund Direct Growth",
  "confidence": 0.89
}
```

**Response (Advice Refusal)**:
```json
{
  "type": "refusal",
  "answer": "I can only provide factual information about mutual fund schemes. For investment advice, please consult a certified financial planner. You can learn more about expense ratios here: https://www.amfiindia.com",
  "source": "https://www.amfiindia.com",
  "scheme": null,
  "confidence": 1.0
}
```

### 7.2 GET /sources
**Response**:
```json
{
  "sources": [
    {"scheme": "HDFC Large Cap Fund", "url": "https://groww.in/..."},
    ...
  ]
}
```

### 7.3 GET /health
**Response**:
```json
{
  "status": "healthy",
  "chunks_loaded": 42,
  "embedding_model": "all-MiniLM-L6-v2",
  "vector_db": "chroma"
}
```

---

## 8. Error Handling

| Scenario | Handling |
|----------|----------|
| Empty query | Return "Please enter a question." |
| No chunks above threshold | Return "I couldn't find specific information about that. Try asking about expense ratio, exit load, minimum SIP, benchmark, or risk level." |
| ChromaDB not initialized | Auto-trigger rebuild on first query |
| Invalid scheme name | Return list of available schemes |
| PII detected in query | Strip and respond with privacy notice |

---

## 9. Security & Privacy

- **No PII storage**: System does not store any user data
- **No authentication**: Demo only, no sensitive data
- **Input sanitization**: Strip HTML/JS from user input
- **CORS**: Disabled (same-origin only)
- **Rate limiting**: None (local demo)

---

## 10. Deployment Architecture (Local)

```
┌─────────────────────────────────────────┐
│           User Browser                  │
│         http://localhost:5000           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Flask Server                  │
│         (localhost:5000)                │
│  ┌─────────────────────────────────┐    │
│  │  RAG Engine (in-process)        │    │
│  │  - ChromaDB (local file)        │    │
│  │  - MiniLM-L6-v2 (in-memory)     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

*End of Architecture Document*
