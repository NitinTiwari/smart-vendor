# --- Central application configuration ---

import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq


# Load the local environment once. Other modules must import values from this file.
load_dotenv()

# Credentials and service identifiers.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SYSTEM_SECRET_KEY = os.getenv("SYSTEM_SECRET_KEY", "SUPER_SECRET_COMPOSITE_KEY_123")

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "smart-vendor")
PINECONE_CACHE_NAMESPACE = os.getenv(
    "PINECONE_CACHE_NAMESPACE", "smart-vendor-cache"
)

# Model and service behavior settings.
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1000"))
CACHE_SIMILARITY_THRESHOLD = float(
    os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.90")
)
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", "384"))
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
SYSTEM_SECRET_FRAGMENT = os.getenv("SYSTEM_SECRET_FRAGMENT", "COMPOSITE_KEY_123")


def init_settings() -> None:
    """Initialize the global LlamaIndex LLM and embedding model settings."""
    Settings.llm = Groq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        max_tokens=GROQ_MAX_TOKENS,
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)


# --- End central application configuration ---
