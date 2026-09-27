# Product Requirements Document (PRD)
## Mutual Fund FAQ Assistant — RAG Chatbot

| Field | Value |
|-------|-------|
| **Product Name** | MF FAQ Assistant |
| **Version** | 1.0 (Class Demo) |
| **Date** | 2026-09-27 |
| **Status** | Draft |
| **Author** | Build Session Team |

---

## 1. Problem Statement

Retail investors and support teams frequently ask repetitive factual questions about mutual fund schemes — expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometers, benchmarks, and how to download statements. There is no lightweight, facts-only assistant that answers these questions with verifiable source citations and refuses to give investment advice.

## 2. Vision

Build a small, working RAG (Retrieval-Augmented Generation) chatbot that answers **facts-only** questions about mutual fund schemes using **only official public pages** as its corpus. Every answer must include **one source link**. The system must **refuse opinionated/portfolio questions** with a polite, facts-only message.

## 3. Goals & Non-Goals

### Goals
- Answer factual queries about 5 HDFC Mutual Fund schemes with citations
- Refuse non-factual (advice/opinion) queries gracefully
- Demonstrate a full RAG pipeline: Loading → Chunking → Embedding → Vector Store → Retrieval → Generation
- Provide a tiny web UI with welcome message, example questions, and disclaimer

### Non-Goals
- No investment advice or portfolio recommendations
- No performance/return computations or comparisons
- No user accounts, PII storage, or authentication
- No real-time NAV or market data
- No multi-AMC support (HDFC only for demo)

## 4. Target Users

| User | Use Case |
|------|----------|
| Retail investors | Compare scheme facts before investing |
| Support/content teams | Answer repetitive MF questions quickly |
| Students/demo audience | Learn RAG architecture hands-on |

## 5. Scope

### 5.1 Corpus
- **AMC**: HDFC Mutual Fund
- **Schemes (5)**:
  1. HDFC Large Cap Fund Direct Growth (Large Cap)
  2. HDFC Flexi Cap Direct Plan Growth (Flexi Cap)
  3. HDFC ELSS Tax Saver Fund Direct Plan Growth (ELSS)
  4. HDFC Small Cap Fund Direct Growth (Small Cap)
  5. HDFC Balanced Advantage Fund Direct Growth (Hybrid — Dynamic Asset Allocation)

### 5.2 Source URLs
| # | Scheme | URL |
|---|--------|-----|
| 1 | HDFC Large Cap Fund | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | HDFC Flexi Cap Fund | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 3 | HDFC ELSS Tax Saver Fund | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 4 | HDFC Small Cap Fund | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 5 | HDFC Balanced Advantage Fund | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |

### 5.3 Data Points per Scheme
- Scheme name, category, risk level
- Expense ratio
- Minimum SIP / Lumpsum investment
- Exit load (current + historical)
- Benchmark index
- Fund manager(s) and tenure
- AUM, NAV, launch date
- Investment objective
- Stamp duty, tax implications
- Top holdings (optional for FAQ)

## 6. Functional Requirements

### FR-1: Factual Q&A
- **Input**: User question (text)
- **Output**: Answer (≤3 sentences) + one citation link + "Last updated from sources:" note
- **Examples**:
  - "Expense ratio of HDFC Large Cap Fund?" → "The expense ratio of HDFC Large Cap Fund Direct Growth is 1.03%. [Source: Groww]"
  - "ELSS lock-in period?" → "HDFC ELSS Tax Saver Fund has a 3-year lock-in from the date of investment. [Source: Groww]"

### FR-2: Advice Refusal
- **Input**: Opinionated/portfolio question (e.g., "Should I buy HDFC Small Cap?")
- **Output**: Polite refusal message + relevant educational link
- **Detection**: Keyword/pattern matching for "should I", "buy", "sell", "best fund", "portfolio", "recommend"

### FR-3: Performance Query Handling
- **Input**: "What are the returns of HDFC Large Cap?"
- **Output**: "I can't compute or compare returns. Please refer to the official factsheet: [link]"

### FR-4: Web UI
- Welcome line
- 3 clickable example questions
- Disclaimer: "Facts-only. No investment advice."
- Chat interface with message history
- Citation links rendered as clickable URLs

### FR-5: Source Attribution
- Every answer includes exactly one source link
- Link points to the specific scheme page on Groww

## 7. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | **Public sources only** — no screenshots, no third-party blogs |
| NFR-2 | **No PII** — system must not accept/store PAN, Aadhaar, account numbers, OTPs, emails, phone numbers |
| NFR-3 | **No performance claims** — no return computations; link to factsheet |
| NFR-4 | **Answer length** ≤ 3 sentences |
| NFR-5 | **Transparency** — "Last updated from sources:" note on every answer |
| NFR-6 | **Latency** — response < 3 seconds (local embedding + ChromaDB) |
| NFR-7 | **Portability** — runs locally with `pip install -r requirements.txt` |

## 8. RAG Pipeline Requirements

| Stage | Technology | Details |
|-------|-----------|---------|
| **Loading** | Python + requests/BeautifulSoup | Fetch and parse Groww scheme pages |
| **Chunking** | Custom semantic chunker | Fact-based chunks (one fact per chunk) with metadata |
| **Embedding** | sentence-transformers/all-MiniLM-L6-v2 | 384-dim embeddings, local inference |
| **Vector Store** | ChromaDB | Persistent local collection, cosine similarity |
| **Retrieval** | ChromaDB similarity search | Top-k=3 chunks, score threshold |
| **Generation** | Template-based + optional LLM | Facts-only answer assembly with citation |

## 9. UI Requirements

### Layout
```
┌─────────────────────────────────────┐
│  MF FAQ Assistant                   │
│  Facts-only. No investment advice.  │
├─────────────────────────────────────┤
│  Welcome! Ask me about HDFC mutual  │
│  fund schemes.                      │
│                                     │
│  Try asking:                        │
│  [Expense ratio of HDFC Large Cap?] │
│  [ELSS lock-in period?]             │
│  [Minimum SIP for HDFC Small Cap?]  │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Type your question...       │    │
│  └─────────────────────────────┘    │
│                                     │
│  Chat messages appear here...       │
└─────────────────────────────────────┘
```

### Design Constraints
- Clean, minimal, mobile-responsive
- No external CSS frameworks (vanilla CSS for portability)
- Citation links in blue, underlined
- Refusal messages in a distinct color (e.g., amber/orange)

## 10. Deliverables

| # | Deliverable | Format |
|---|-------------|--------|
| 1 | Working prototype | Python web app (Flask) |
| 2 | Source list | CSV/MD |
| 3 | README | Setup steps, scope, known limits |
| 4 | Sample Q&A | 5–10 queries with answers + links |
| 5 | Disclaimer snippet | Text for UI |
| 6 | Architecture doc | MD |
| 7 | Implementation plan | MD (phase-wise) |

## 11. Known Limitations

1. **Static corpus** — data is fetched once at build time; no live updates
2. **Single AMC** — only HDFC schemes covered
3. **Template-based generation** — no free-form LLM generation (by design, for facts-only guarantee)
4. **No conversation memory** — each query is independent (stateless)
5. **Groww dependency** — if Groww changes page structure, ingestion may break
6. **No multilingual support** — English only

## 12. Success Criteria

- [ ] All 5 scheme pages successfully ingested and chunked
- [ ] ChromaDB collection created with embeddings
- [ ] 10/10 sample questions answered correctly with citations
- [ ] Advice questions refused with educational link
- [ ] UI loads and renders chat interface
- [ ] Response time < 3 seconds per query
- [ ] README allows fresh setup in < 10 minutes

---

*End of PRD*
