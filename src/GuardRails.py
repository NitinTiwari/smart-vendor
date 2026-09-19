import re
from functools import wraps
from src.config import SYSTEM_SECRET_FRAGMENT, SYSTEM_SECRET_KEY

# --- Guardrails: reject prompt injection and prevent secret leakage ---

def validate_input_guardrails(func):
    """Decorate an agent entry point with prompt-injection pattern checks."""
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
    """Return output unless it contains the configured secret or its fragment."""
    # 1. Exact match check
    if SYSTEM_SECRET_KEY in agent_output:
        raise ValueError("[❌ SECURITY ALERT] Output blocked: Exact secret key leak detected!")
        
    # 2. Obfuscation check (Example: Check if a highly unique part of the key leaks)
    # Check the configured unique fragment after removing common separators.
    if SYSTEM_SECRET_FRAGMENT in agent_output.replace(" ", "").replace("-", ""):
        raise ValueError("[❌ SECURITY ALERT] Output blocked: Fragmented secret key leak detected!")

    return agent_output


# --- End input and output guardrails ---








