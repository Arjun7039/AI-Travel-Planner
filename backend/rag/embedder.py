from chromadb import Client
from sentence_transformers import SentenceTransformer

def get_chroma_collection():
    client = Client()
    try:
        collection = client.get_collection("travel_knowledge")
    except ValueError:
        collection = client.create_collection("travel_knowledge")
    return collection

def embed_documents(docs: list[str], ids: list[str], metadatas: list[dict] = None):
    print("🧠 Embedding documents into ChromaDB...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    collection = get_chroma_collection()
    
    embeddings = model.encode(docs).tolist()
    
    collection.upsert(
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print("✅ Documents embedded successfully.")

def load_mock_corpus():
    """Initializes the collection with some mock travel data."""
    mock_docs = [
        "Goa is famous for its beaches like Baga and Calangute, and vibrant nightlife. Local tip: Visit the secret sunset point near Anjuna.",
        "Bengaluru is known as the Silicon Valley of India, but has great breweries and traffic. Must try food: CTR Benne Masala Dosa.",
        "Jaipur offers rich history with the Amber Fort and City Palace. Local tip: Shop for handicrafts at Bapu Bazaar.",
        "Kerala backwaters in Alleppey provide a serene houseboat experience. Best to visit from October to March."
    ]
    ids = [f"doc_{i}" for i in range(len(mock_docs))]
    embed_documents(mock_docs, ids)
