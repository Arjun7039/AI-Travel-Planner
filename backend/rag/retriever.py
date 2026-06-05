from backend.rag.embedder import get_chroma_collection
from sentence_transformers import SentenceTransformer

# Load the RAG model globally once to eliminate the 3-second load latency on every request
_rag_model = None

def get_rag_model():
    global _rag_model
    if _rag_model is None:
        _rag_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _rag_model

def retrieve_context(query: str, n_results: int = 3) -> str:
    """Retrieve relevant context from ChromaDB for a given query."""
    try:
        model = get_rag_model()
        query_embedding = model.encode([query]).tolist()
        
        collection = get_chroma_collection()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        if results and results["documents"] and results["documents"][0]:
            return "\n".join(results["documents"][0])
        return "No relevant context found in database."
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return ""
