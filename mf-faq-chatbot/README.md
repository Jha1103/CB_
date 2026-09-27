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
│   ├── raw_pages/          # Raw HTML from Groww
│   ├── structured_facts.json
│   └── chunks.json
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
