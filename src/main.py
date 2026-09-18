import asyncio
from src.config import init_settings
from src.cache import check_cache, update_cache
from src.tools import get_agent_tools
from llama_index.core.agent.workflow import AgentWorkflow, ReActAgent
from src.GuardRails import validate_input_guardrails, validate_output_guardrails

@validate_input_guardrails
async def run_vendor_intelligence_agent(user_input: str):
    # Step A: Validate against the cache layer to preserve tokens
    cached_response = check_cache(user_input)
    if cached_response:
        print("\n⚡ [CACHE HIT] Returning response instantly from local storage:")
        return cached_response
        
    print("\n❄️ [CACHE MISS] Activating ReAct Agent workflow via Groq...")
    
    # Get tools and configure the agent runtime
    tools = get_agent_tools()
    
    vendor_agent = ReActAgent(
        name="vendor_risk_analyst",
        description="Analyzes supplier risks using corporate databases and real-time news search tools.",
        tools=tools
    )
    
    workflow = AgentWorkflow(agents=[vendor_agent], root_agent=vendor_agent.name)
    
    # Execute the agent loop
    result = await workflow.run(user_msg=user_input)
    final_answer = str(result)
    
    # Update cache for subsequent entries
    update_cache(user_input, final_answer)
    return final_answer

async def main():
    init_settings()
    print("--- Smart-Vendor Market Intelligence System Activated ---")
    
    while True:
        query = input("\nEnter your supplier risk query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        try:
            answer = await run_vendor_intelligence_agent(query)
            # Validate output against guardrails before displaying
            safe_answer = validate_output_guardrails(answer)
            print("\n--- Final Profile Matrix ---")
            print(safe_answer)
        except Exception as e:
            print(f"An execution error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
