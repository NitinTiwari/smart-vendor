import os
from pinecone import Pinecone
from llama_index.core import Settings

# Fetch the global properties
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "smart-vendor")
CACHE_NAMESPACE = os.getenv("PINECONE_CACHE_NAMESPACE", "smart-vendor-cache")

# Minimum similarity threshold to determine a cache hit (0.90 = highly identical)
SIMILARITY_THRESHOLD = 0.90

def get_cache_client():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)

def check_cache(query: str) -> str | None:
    """Computes the embedding of the query and looks for a semantic hit in Pinecone."""
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
        if match["score"] >= SIMILARITY_THRESHOLD:
            print(f"🎯 [SEMANTIC CACHE HIT] Match Score: {match['score']:.4f}")
            return match["metadata"]["response_text"]
            
    return None

def update_cache(query: str, response: str):
    """Saves the query vector and text answer to Pinecone for future checks."""
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
