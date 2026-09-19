from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research.base import TavilyToolSpec
from src.database import get_pinecone_index
from src.config import TAVILY_API_KEY

# --- Agent tools: internal vendor retrieval, web research, and utilities ---

async def query_internal_vendor_data(query_str: str) -> str:
    """Search private vendor records for supplier history and contract evidence."""
    index = get_pinecone_index()
    query_engine = index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(query_str)
    print(f"🔍 [RAG QUERY] Retrieved {len(response.source_nodes)} relevant documents for the query.")
    return str(response)

def add_tools(a: int, b: int) -> int:
    """Return the sum of two integers for agent tool demonstrations."""
    print(f"Adding {a} and {b} together.")
    return a + b

def get_agent_tools() -> list:
    """Build the internal, web-search, and arithmetic tools for the agent."""
    # Wrap the RAG async function into a LlamaIndex Tool
    rag_tool = FunctionTool.from_defaults(async_fn=query_internal_vendor_data)
    
    # 2. Live Web Search Tool Fallback
    tavily_spec = TavilyToolSpec(api_key=TAVILY_API_KEY)
    web_tools = tavily_spec.to_tool_list()

    add_tool= FunctionTool.from_defaults(fn=add_tools, name="add_numbers", description="Adds two numbers together.")
    
    return [rag_tool] + web_tools + [add_tool]


# --- End agent tool definitions ---
