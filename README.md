# Smart Vendor

Smart Vendor is an AI-powered supplier risk and vendor intelligence assistant. It helps users evaluate vendors by combining:

- private internal vendor knowledge stored in Pinecone vector search,
- live web research via Tavily,
- semantic caching to reduce repeated LLM cost and latency,
- prompt-injection and secret-leak guardrails to protect enterprise usage,
- a ReAct-style LlamaIndex agent to reason over structured and unstructured data.

This project is designed for business users who need a fast vendor-risk assessment before entering contracts, launching purchases, or onboarding suppliers.

---

## What this system does

The application accepts a natural-language query such as:

- "Is my supplier Nexus Logistics Inc. healthy to begin a new deal?"
- "Should I sign a deal with Vertex Chipsets Ltd.?"
- "Assess the risk profile of this supplier before procurement approval."

It then:

1. Validates the input for malicious prompt injection patterns.
2. Checks a semantic cache in Pinecone for a similar prior query.
3. Runs a ReAct AI agent that can access internal vendor data and live web research tools.
4. Retrieves relevant supplier facts from stored vector documents.
5. Combines evidence from internal records and external sources.
6. Applies output validation to prevent accidental secret leakage.
7. Returns a clear answer to the user.

---

## End-to-end data flow

The actual runtime flow in this project is:

1. User enters a supplier question in the CLI.
2. `src/main.py` calls `run_vendor_intelligence_agent(user_input)`.
3. The input is wrapped by `@validate_input_guardrails` from `src/GuardRails.py`.
4. `check_cache(user_input)` in `src/cache.py` computes the embedding for the query and searches Pinecone for a near-identical cached response.
5. If the semantic similarity score is above the configured threshold (`0.90`), the answer is returned immediately from cache.
6. If there is no relevant cache hit, the system initializes the agent runtime via `src/config.py`.
7. `src/tools.py` creates the tool list:
   - `query_internal_vendor_data()` for internal supplier document retrieval via Pinecone RAG,
   - Tavily search tools for web research,
   - a demonstration arithmetic tool.
8. A `ReActAgent` is created in `src/main.py` using LlamaIndex.
9. The agent executes the workflow and calls appropriate tools based on the user request.
10. The final answer is stringified and sent to `update_cache()` so future similar queries can be served faster.
11. `validate_output_guardrails()` checks the final response before printing it to the terminal.
12. The result is displayed to the user in the console.

This architecture reduces repeated LLM cost and preserves quick results for common queries while still allowing full reasoning for new questions.

---

## Technology stack

### Core application

- Python 3.13+
- LlamaIndex
- Groq LLM integration
- HuggingFace embedding model
- Pinecone vector database
- Tavily search API
- Python dotenv

### Main libraries

- `llama-index-core`
- `llama-index-llms-groq`
- `llama-index-embeddings-huggingface`
- `llama-index-vector-stores-pinecone`
- `llama-index-tools-tavily`
- `pinecone-client`
- `python-dotenv`

### AI stack in practice

- LLM model: `qwen/qwen3.8-27b` hosted through Groq
- Embedding model: `BAAI/bge-small-en-v1.5`
- Vector index: Pinecone serverless index
- Search/research: Tavily

---

## Project structure

```text
smart-vendor/
├── README.md
├── pyproject.toml
├── requirements.txt
├── vendor_query_cache.json
├── src/
│   ├── GuardRails.py
│   ├── cache.py
│   ├── config.py
│   ├── database.py
│   ├── ingest.py
│   ├── main.py
│   ├── tools.py
│   └── smart_vendor/
│       └── __init__.py
└── .env.example (recommended to create locally)
```

### File responsibilities

- `src/main.py` — CLI entry point and orchestration loop
- `src/config.py` — environment setup and model configuration
- `src/tools.py` — agent tool definitions and vector search wrappers
- `src/database.py` — Pinecone index creation and connection logic
- `src/cache.py` — semantic caching using vector similarity
- `src/GuardRails.py` — prompt injection and secret leak protections
- `src/ingest.py` — sample vendor document ingestion into Pinecone
- `vendor_query_cache.json` — legacy or sample cache file present in the repository

---

## Setup and installation

### 1. Clone or open the project

```bash
git clone <repo-url>
cd smart-vendor
```

### 2. Create a virtual environment

Using Python 3.13 or later:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

You can also use the project metadata defined in `pyproject.toml` if you use `uv`:

```bash
uv sync
```

---

## Required environment variables

Create a `.env` file in the project root with the following values:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=smart-vendor
PINECONE_CACHE_NAMESPACE=smart-vendor-cache
SYSTEM_SECRET_KEY=SUPER_SECRET_COMPOSITE_KEY_123
```

### Variable meanings

- `GROQ_API_KEY` — API key for Groq-hosted LLM access
- `TAVILY_API_KEY` — API key for Tavily live web search and research
- `PINECONE_API_KEY` — Pinecone credentials for vector data storage
- `PINECONE_INDEX_NAME` — name of the Pinecone index used for vendor records and cache
- `PINECONE_CACHE_NAMESPACE` — namespace used for the semantic cache
- `SYSTEM_SECRET_KEY` — secret used by the output guardrail to block accidental leakage

> Important: keep API keys out of source control. Do not commit the `.env` file to Git.

---

## Running the app

Start the interactive vendor intelligence CLI:

```bash
python src/main.py
```

Or, if using the module layout correctly from the project root:

```bash
python -m src.main
```

When the program starts, it will prompt:

```text
Enter your supplier risk query (or 'exit' to quit):
```

Example prompts:

```text
Is my supplier Nexus Logistics Inc. healthy to begin a new deal?
Should I pursue a deal with Vertex Chipsets Ltd.?
What is the risk profile of Apex Industrial Chemicals?
```

---

## Indexing vendor knowledge

To populate the Pinecone index with sample supplier records, run:

```bash
python src/ingest.py
```

This script:

- initializes the model settings,
- connects to Pinecone,
- creates the vector index if needed,
- generates mock vendor documents,
- embeds the documents,
- uploads them to Pinecone.

This is useful for demo purposes and testing the retrieval pipeline before onboarding real supplier data.

---

## Cache behavior

The project includes a semantic cache layer in `src/cache.py`.

### How it works

- The user query is converted to an embedding using `Settings.embed_model`.
- A Pinecone similarity query searches the configured cache namespace.
- If a match exceeds `0.90`, it is treated as a semantically equivalent prior query.
- The cached response is returned immediately.

### Why it matters

This helps:

- reduce LLM token usage,
- lower latency for repeated questions,
- maintain a faster experience for common vendor inquiries.

---

## Guardrails and safety design

This project includes two safety checks:

### Input guardrails

Implemented in `src/GuardRails.py` using a decorator.

They block obvious prompt-injection patterns such as:

- "ignore previous instructions"
- "system prompt"
- "act as an unrestricted assistant"
- "bypass restrictions"

This helps reduce the risk of a malicious query hijacking the reasoning flow.

### Output guardrails

The output validation checks for accidental secret exposure in model-generated text. If the configured `SYSTEM_SECRET_KEY` appears in the output, the application raises a security exception.

This is especially helpful for enterprise applications where model outputs must not reveal sensitive internal credentials or system secrets.

---

## Agent tools and retrieval

The `ReActAgent` gets a set of tools from `src/tools.py`.

### Internal vendor search tool

`query_internal_vendor_data(query_str)` performs a Pinecone vector retrieval over stored vendor records and returns the most relevant supplier context.

### Web research tool

The project loads Tavily search tools to allow the agent to perform live web-based research when the internal knowledge base is incomplete or when external information is needed.

### Demo tool

There is also a simple arithmetic tool (`add_numbers`) included for demonstration/testing.

---

## Example workflow

A typical end-user flow looks like this:

```text
User: "Should I have a deal with supplier Vertex Chipsets Ltd.?"

System:
  - Input passes guardrails
  - Cache check on query embedding
  - No match found
  - ReAct agent runs
  - Internal Pinecone vector search retrieves risk data
  - Tavily web tool may supplement with current public information
  - Final answer generated
  - Output validated
  - Response printed to user
```

The output may include supplier status, financial risk, compliance issues, regulatory exposure, and recommendations.

---

## Current project status

This repository is a working prototype and AI assistant for supplier-vendor assessment. It is best suited for:

- internal proof-of-concept demos,
- procurement risk analysis experiments,
- supplier onboarding reviews,
- AI-assisted due diligence prototypes.

It is not yet a full enterprise-grade production platform with:

- user authentication,
- role-based access control,
- dashboard UI,
- multilingual support,
- full document ingestion pipeline for PDFs, CSVs, or ERP exports,
- persistent enterprise audit logging.

---

## Suggested next improvements

To turn this into a production-ready vendor intelligence system, consider adding:

1. A proper web or API front end for non-technical users.
2. Real supplier document ingestion from PDF/Excel/CSV files.
3. Authentication and authorization for internal users.
4. Structured output schemas for audit-grade reports.
5. Database-backed historical case tracking.
6. More advanced scoring models for vendor risk and ESG compliance.
7. Better observability with logs, metrics, and request tracing.
8. A richer cache strategy with TTL and expiration policies.

---

## Troubleshooting

### Missing API keys

If the app fails to connect to Groq, Pinecone, or Tavily, verify that your `.env` file contains all required keys and that they are loaded correctly with `python-dotenv`.

### Pinecone connection issues

Check that:

- your Pinecone API key is valid,
- the target index exists or can be created,
- the index name is spelled correctly,
- the selected region/cloud is available for your account.

### No search results returned

This may happen if:

- the Pinecone index is empty,
- the embedding model is not initialized correctly,
- the documents were not ingested yet,
- the query is too vague or outside the knowledge base scope.

Run `python src/ingest.py` first to seed the vector database with sample vendor documents.

---

## License

This project does not currently declare a specific license. If you plan to distribute or deploy it commercially, add a license file such as MIT or Apache 2.0 before production use.

---

## Summary

Smart Vendor combines LlamaIndex agent orchestration, Groq LLM reasoning, Pinecone vector search, semantic caching, and guide rails to create a practical vendor intelligence assistant. It is designed to answer supplier-risk questions quickly and safely while allowing deeper reasoning for new or uncertain queries.

For a quick demo, install dependencies, add your environment variables, run `python src/ingest.py`, and then launch the interactive prompt with `python src/main.py`.
