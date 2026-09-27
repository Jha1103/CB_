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
    session_id = data.get("session_id", "default")

    if not query:
        return jsonify({
            "type": "error",
            "answer": "Please enter a question.",
            "source": None,
        })

    result = process_query(query, session_id)
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
