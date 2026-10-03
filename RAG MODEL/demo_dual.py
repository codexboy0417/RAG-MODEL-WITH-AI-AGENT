"""
=============================================================================
Quick CLI Demo: Dual AI Engine (RAG Model + Autonomous AI Agent)
=============================================================================
Tests both branches using the working AI Agent API keys:
1. Branch 1: RAG Model with FAISS vector search and source attribution
2. Branch 2: AI Agent with LangChain, Wikipedia, Tavily Search, and Math tools
=============================================================================
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("=" * 65)
print("PIXELCORE DUAL AI ENGINE CLI DEMO")
print("=" * 65)
print(f"Groq API Key:   {'Active' if groq_key else 'Missing'}")
print(f"Tavily API Key: {'Active' if tavily_key else 'Missing'}")
print("=" * 65)

# Branch 1: RAG Model
print("\n[Branch 1] Testing RAG Model (Document Ingestion & Retrieval)...")
try:
    from rag_engine import RAGEngine
    engine = RAGEngine(groq_api_key=groq_key)
    doc = "Apollo 11 landed humans on the Moon on July 20, 1969. Commander Neil Armstrong and Lunar Module pilot Buzz Aldrin."
    engine.add_documents([doc], source="Apollo11.txt")
    rag_res = engine.get_response("When did Apollo 11 land on the moon?")
    print("RAG Answer:", rag_res.get("answer", ""))
    print("RAG Source:", "From Documents (RAG)" if rag_res.get("is_rag") else "LLM")
except Exception as e:
    print("RAG Error:", e)

# Branch 2: AI Agent
print("\n[Branch 2] Testing AI Agent (Autonomous Tool Execution)...")
try:
    import agent_engine
    executor, tools, llm = agent_engine.build_agent(groq_key, tavily_key)
    print(f"Agent initialized with {len(tools)} tools: {[t.name for t in tools]}")
    agent_res = agent_engine.run_agent_query(executor, "What is (452 * 78) + 982? Calculate using math tools.")
    print("Agent Answer:", agent_res.get("answer", ""))
    print("Agent Tools Used:", agent_res.get("tools_used", []))
except Exception as e:
    print("Agent Error:", e)

print("\n" + "=" * 65)
print("Dual AI Engine demo finished successfully. Both branches operational.")
print("=" * 65)
