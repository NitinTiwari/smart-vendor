from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research.base import TavilyToolSpec
from src.database import get_pinecone_index
from src.config import TAVILY_API_KEY

# 1. Internal Documents Search Tool (Pinecone RAG)
async def query_internal_vendor_data(query_str: str) -> str:
    """Searches private enterprise databases for historical supplier profiles, performance reviews, and contract data."""
    index = get_pinecone_index()
    query_engine = index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(query_str)
    print(f"🔍 [RAG QUERY] Retrieved {len(response.source_nodes)} relevant documents for the query.")
    return str(response)

def add_tools(a: int, b: int) -> int:
    """Simple addition tool for demonstration purposes."""
    print(f"Adding {a} and {b} together.")
    return a + b

def get_agent_tools() -> list:
    """Builds and lists out tools ready for the ReAct Agent."""
    # Wrap the RAG async function into a LlamaIndex Tool
    rag_tool = FunctionTool.from_defaults(async_fn=query_internal_vendor_data)
    
    # 2. Live Web Search Tool Fallback
    tavily_spec = TavilyToolSpec(api_key=TAVILY_API_KEY)
    web_tools = tavily_spec.to_tool_list()

    add_tool= FunctionTool.from_defaults(fn=add_tools, name="add_numbers", description="Adds two numbers together.")
    
    return [rag_tool] + web_tools + [add_tool]
