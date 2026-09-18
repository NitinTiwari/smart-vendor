import os
import re
from functools import wraps

# --- INPUT GUARDRAIL (Fixed Decorator Structure) ---

def validate_input_guardrails(func):
    """
    Decorator guardrail to prevent prompt injection before the agent runs.
    """
    # Compiled regex is faster for repeated checks
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(your\s+)?previous\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt", re.IGNORECASE),
        re.compile(r"act\s+as\s+an?\s+unrestricted", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+unfiltered", re.IGNORECASE),
        re.compile(r"bypass\s+restrictions", re.IGNORECASE),
    ]

    @wraps(func)
    def wrapper(user_input: str, *args, **kwargs):
        # 1. Check heuristics/regex
        for pattern in INJECTION_PATTERNS:
            if pattern.search(user_input):
                raise ValueError("[❌ SECURITY ALERT] Input blocked: Potential prompt injection detected.")
        
        # Future-proofing: You can add an LLM-based scanner or vector check here
        
        return func(user_input, *args, **kwargs)
    return wrapper


# --- OUTPUT GUARDRAIL (Robust Secret Detection) ---

def validate_output_guardrails(agent_output: str) -> str:
    """
   "You are a strict security guard for an enterprise application. "
    "Analyze the user's input. If the user is asking for jokes, poems, casual chit-chat, "
    "or anything unrelated to business/professional assistance, reply with 'BLOCK'. "
    "Otherwise, reply with 'ALLOW'.\n\n"
    "User Input: {agent_output}\n"
    "Decision (BLOCK or ALLOW):"
    """
    # Fetch from environment variable instead of hardcoding
    SYSTEM_SECRET_KEY = os.getenv("SYSTEM_SECRET_KEY", "SUPER_SECRET_COMPOSITE_KEY_123")
    
    # 1. Exact match check
    if SYSTEM_SECRET_KEY in agent_output:
        raise ValueError("[❌ SECURITY ALERT] Output blocked: Exact secret key leak detected!")
        
    # 2. Obfuscation check (Example: Check if a highly unique part of the key leaks)
    # If your key is "SUPER_SECRET_COMPOSITE_KEY_123", check for the unique core identifier
    unique_fragment = "COMPOSITE_KEY_123"
    if unique_fragment in agent_output.replace(" ", "").replace("-", ""):
        raise ValueError("[❌ SECURITY ALERT] Output blocked: Fragmented secret key leak detected!")

    return agent_output



