from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from src.config import (
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_DIMENSION,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
)


# --- Database: Pinecone vector index creation and access ---


def get_pinecone_index():
    """Get or create the configured Pinecone index used for vendor retrieval."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # 1. Initialize or create the underlying Pinecone infrastructure
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        # Create a brand new index if it doesn't exist
        pc.create_index(
            name=PINECONE_INDEX_NAME, 
            dimension=PINECONE_DIMENSION,
            metric="cosine", 
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
        )
    
    # 2. Connect to the Pinecone index (runs whether index is new or existing)
    pinecone_index = pc.Index(name=PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # 3. Handle LlamaIndex initialization based on existence
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        # BRAND NEW INDEX: Setup standard storage context for ingestion
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, 
            storage_context=storage_context
        )
    else:
        # EXISTING INDEX: Load existing data directly from the vector store
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        
    return index


    # --- End Pinecone database operations ---
