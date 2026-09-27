"""Flask web application for MF FAQ Assistant."""
import os
import sys

# Memory optimization: set before any imports
os.environ.setdefault("TORCH_DEVICE", "cpu")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    """Render the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Process a chat message."""
    # Lazy import to avoid loading heavy modules at startup
    from src.pipeline import process_query

    data = request.get_json()
    query = data.get("query", "").strip()
    session_id = data.get("session_id", "default")

    if not query:
        return jsonify({
            "type": "error",
            "answer": "Please enter a question.",
            "source": None,
        })

    try:
        result = process_query(query, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "type": "error",
            "answer": f"Error: {str(e)}",
            "source": None,
        }), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "chunks_loaded": "lazy",
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_db": "chroma",
    })


@app.route("/sources")
def sources():
    """List source URLs."""
    from src.config import SOURCE_URLS
    return jsonify({"sources": SOURCE_URLS})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
