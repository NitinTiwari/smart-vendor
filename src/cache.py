from pinecone import Pinecone
from llama_index.core import Settings
from src.config import (
    CACHE_SIMILARITY_THRESHOLD,
    PINECONE_API_KEY,
    PINECONE_CACHE_NAMESPACE,
    PINECONE_INDEX_NAME,
)

# --- Semantic cache: Pinecone-backed query and response storage ---

CACHE_NAMESPACE = PINECONE_CACHE_NAMESPACE


def get_cache_client():
    """Create and return a Pinecone index client for the semantic cache."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)


def check_cache(query: str) -> str | None:
    """Find a sufficiently similar cached response for a vendor query."""
    index = get_cache_client()
    
    # Generate the query embedding vector using your default BGE model
    query_vector = Settings.embed_model.get_query_embedding(query)
    
    # Query only inside the dedicated cache namespace
    response = index.query(
        namespace=CACHE_NAMESPACE,
        vector=query_vector,
        top_k=1,
        include_metadata=True
    )
    
    # Check if a close semantic result was found
    if response.get("matches"):
        match = response["matches"][0]
        if match["score"] >= CACHE_SIMILARITY_THRESHOLD:
            print(f"🎯 [SEMANTIC CACHE HIT] Match Score: {match['score']:.4f}")
            return match["metadata"]["response_text"]
            
    return None


def update_cache(query: str, response: str):
    """Store a query embedding and its response in the configured cache namespace."""
    index = get_cache_client()
    
    # Generate the embedding vector
    query_vector = Settings.embed_model.get_query_embedding(query)
    
    # Use a deterministic ID string generated from the query text length/hash
    vector_id = f"cache_{hash(query)}"
    
    # Store vector and map the plain text as string metadata properties
    index.upsert(
        vectors=[
            {
                "id": vector_id,
                "values": query_vector,
                "metadata": {
                    "query_text": query,
                    "response_text": response
                }
            }
        ],
        namespace=CACHE_NAMESPACE
    )
    print("💾 Saved response structure into Pinecone semantic cache.")


# --- End semantic cache operations ---
