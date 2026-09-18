import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

# Global variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "smart-vendor")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def init_settings():
    """Initialises global LlamaIndex model configurations."""
    # Use Llama 3.3 70B on Groq for heavy tool usage and complex analytical flows
    Settings.llm = Groq(
        model="qwen/qwen3.8-27b", 
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=1000
    )
    # Fast, high-quality open-source text embedding
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
