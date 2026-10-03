"""
=============================================================================
Quick CLI Demo: RAG Model with Groq and Source Attribution
=============================================================================
This script demonstrates how to use the RAGEngine directly in Python
(similar to a Google Colab notebook environment).

Flow:
1. Load Groq API key from environment (.env) or prompt user.
2. Initialize RAGEngine.
3. Add a sample document or extract from PDF / Image.
4. Ask a question present in the document -> Verify it shows RAG source.
5. Ask an out-of-context question -> Verify it shows pure LLM source.
=============================================================================
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles so emojis print without errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from rag_engine import RAGEngine

# Step 1: Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "your_groq_api_key_here":
    print("=" * 60)
    print("GROQ_API_KEY not found in .env file.")
    api_key = input("Please enter your Groq API Key: ").strip()
    print("=" * 60)

if not api_key:
    print("Error: Groq API Key is required to run this demo.")
    exit(1)

# Step 2: Initialize RAG Engine
print("\n[1/4] Initializing RAGEngine (Loading SentenceTransformer & FAISS)...")
engine = RAGEngine(groq_api_key=api_key)

# Step 3: Ingest sample document into vector store
print("\n[2/4] Ingesting sample knowledge into Vector Store...")
sample_document = """
Project Alpha is a next-generation lunar exploration mission scheduled for launch in November 2027.
The mission commander is Dr. Elena Rostova, and the lead robotics engineer is David Kim.
Project Alpha utilizes an ion propulsion engine designed by Astralis Dynamics and is powered by
a compact thorium-based micro-reactor providing 50 kW of continuous electrical power.
The primary landing site selected is the Shackleton Crater near the lunar South Pole.
"""

chunks_added = engine.add_documents([sample_document], source="Project_Alpha_Brief.txt")
print(f"Successfully chunked and embedded {chunks_added} chunks into FAISS vector database!")

# Step 4: Ask an in-domain question (should be answered via RAG)
print("\n[3/4] Testing In-Context Question (Expected: RAG Source)...")
q1 = "Who is the mission commander for Project Alpha and what engine does it use?"
print(f"Question: {q1}")
res1 = engine.get_response(q1)

print("-" * 50)
print(f"Answer: {res1['answer']}")
print(f"Source Label: {res1['source_label']}")
print(f"Used RAG Context? {res1['is_rag']}")
print("-" * 50)

# Step 5: Ask an out-of-domain question (should be answered via pure LLM)
print("\n[4/4] Testing Out-of-Context Question (Expected: Pure LLM Source)...")
q2 = "What is the capital of France and what is it famous for?"
print(f"Question: {q2}")
res2 = engine.get_response(q2)

print("-" * 50)
print(f"Answer: {res2['answer']}")
print(f"Source Label: {res2['source_label']}")
print(f"Used RAG Context? {res2['is_rag']}")
print("-" * 50)

print("\nDemo completed successfully!")
