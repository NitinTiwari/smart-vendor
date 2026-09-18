import os
import asyncio
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

# Import configurations from your existing modules
from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, init_settings
from src.database import get_pinecone_index

def generate_sample_vendor_data() -> list[Document]:
    """Generates mock corporate vendor records to simulate file parsing (PDF/CSV)."""
    print("Generating mock vendor profiles and compliance histories...")
    
    samples = [
        Document(
            text="""Vendor Profile: Nexus Logistics Inc.
            Status: Preferred Partner. Global shipping and warehouse provider.
            Financial Health Score: 88/100 (Stable operational liquidity).
            Compliance Record: Last passed audit on November 14, 2025. 
            Risk Profile: Minor exposure to labor union negotiations in European ports. No active lawsuits.""",
            metadata={"vendor_name": "Nexus Logistics", "category": "Logistics", "risk_level": "Low"}
        ),
        Document(
            text="""Vendor Profile: Vertex Chipsets Ltd.
            Status: Under Review. Semiconductor and microelectronics manufacturer.
            Financial Health Score: 52/100 (High debt-to-equity ratio, experiencing cash flow strain).
            Compliance Record: Failed environmental waste disposal audit in Q3 2025. Paid a $45,000 fine.
            Risk Profile: High risk. Vulnerable to localized regulatory shutdowns and supply bottlenecks due to raw material dependencies.""",
            metadata={"vendor_name": "Vertex Chipsets", "category": "Manufacturing", "risk_level": "High"}
        ),
        Document(
            text="""Vendor Profile: Apex Industrial Chemicals
            Status: Approved. Chemical distributor and raw material refinery.
            Financial Health Score: 79/100 (Adequate cash reserves).
            Compliance Record: Fully compliant with international safety standards. Passed ISO 9001 audit.
            Risk Profile: Medium risk. Subject to strict regulatory pricing updates. Suffered a 3-day factory halt in January 2026 due to an equipment failure, now fully resolved.""",
            metadata={"vendor_name": "Apex Chemicals", "category": "Raw Materials", "risk_level": "Medium"}
        )
    ]
    return samples

async def upload_documents_to_pinecone():
    # 1. Initialize Groq/Embedding configurations
    init_settings()
    
    # 2. Connect to Pinecone and create index if it doesn't exist
    print(f"Connecting to Pinecone index: '{PINECONE_INDEX_NAME}'...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Target our vector store wrapper
    index = get_pinecone_index()
    
    # 3. Generate documents
    documents = generate_sample_vendor_data()
    
    # 4. Parse, embed, and upsert documents
    print("Converting documents into vector embeddings and uploading to Pinecone...")
    for doc in documents:
        print(f" -> Indexing {doc.metadata['vendor_name']}...")
        index.insert(doc)
        
    print("\n✅ Success! All sample vendor documents successfully uploaded to Pinecone.")

if __name__ == "__main__":
    # Run the ingestion pipeline
    asyncio.run(upload_documents_to_pinecone())
