"""
=============================================================================
Unified AI System: RAG Model & Autonomous AI Agent  |  Streamlit App
=============================================================================

This application provides a dual-branch architecture in the same web interface:
1. Branch 1: RAG Model (Document Q&A with PDF/Image OCR Ingestion & Vector Search)
2. Branch 2: AI Agent (Autonomous Multi-Tool Agent with Tavily, Wikipedia & Math)

Author : Codex_boy
=============================================================================
"""

import os
import tempfile
import traceback
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st

from rag_engine import RAGEngine
import agent_engine


# =============================================================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# =============================================================================
st.set_page_config(
    page_title="Dual AI Engine: RAG Model & AI Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Green badge for RAG-sourced answers */
    .badge-rag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        background-color: #d4edda;
        color: #155724;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Orange badge for AI Agent answers */
    .badge-agent {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        background-color: #ffe8d6;
        color: #d9480f;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Blue badge for general-knowledge answers */
    .badge-llm {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        background-color: #cce5ff;
        color: #004085;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Amber badge for real-time tools */
    .badge-tool {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        background-color: #fff3cd;
        color: #856404;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Styled container for retrieved context snippets */
    .context-box {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 0.85rem;
        line-height: 1.5;
        color: #333;
    }

    /* Styled container for agent tool execution trace */
    .tool-box {
        background-color: #fffaf5;
        border-left: 4px solid #ff7a18;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 0.85rem;
        line-height: 1.5;
        color: #333;
        font-family: monospace;
    }

    /* Subtle divider between chat turns */
    .chat-divider {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 2. SESSION-STATE INITIALISATION
# =============================================================================

if "active_branch" not in st.session_state:
    st.session_state.active_branch = "rag"

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None

if "rag_chat_history" not in st.session_state:
    st.session_state.rag_chat_history = []

if "agent_chat_history" not in st.session_state:
    st.session_state.agent_chat_history = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

if "tavily_api_key" not in st.session_state:
    st.session_state.tavily_api_key = os.getenv("TAVILY_API_KEY", "")


# =============================================================================
# 3. HELPER FUNCTIONS
# =============================================================================

def _initialise_rag_engine(api_key: str) -> RAGEngine:
    if (
        st.session_state.rag_engine is None
        or st.session_state.groq_api_key != api_key
        or not hasattr(st.session_state.rag_engine, "add_document")
    ):
        import importlib
        import tools
        importlib.reload(tools)
        import rag_engine
        importlib.reload(rag_engine)
        st.session_state.rag_engine = rag_engine.RAGEngine(groq_api_key=api_key)
        st.session_state.groq_api_key = api_key
    return st.session_state.rag_engine


def _initialise_agent_executor(groq_key: str, tavily_key: str):
    if (
        st.session_state.agent_executor is None
        or getattr(st.session_state, "_last_agent_groq_key", "") != groq_key
        or getattr(st.session_state, "_last_agent_tavily_key", "") != tavily_key
    ):
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        executor, tools, llm = agent_engine.build_agent(
            groq_key=groq_key,
            tavily_key=tavily_key,
            model_name=model_name
        )
        st.session_state.agent_executor = executor
        st.session_state._last_agent_groq_key = groq_key
        st.session_state._last_agent_tavily_key = tavily_key
    return st.session_state.agent_executor


def _process_uploaded_file(uploaded_file, engine: RAGEngine) -> bool:
    suffix = os.path.splitext(uploaded_file.name)[1]
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        ext = suffix.lower()
        if hasattr(engine, "add_document"):
            engine.add_document(tmp_path, source=uploaded_file.name)
        elif ext == ".pdf" and hasattr(engine, "process_pdf"):
            engine.process_pdf(tmp_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"] and hasattr(engine, "process_image"):
            engine.process_image(tmp_path)
        else:
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                engine.add_documents([f.read()], source=uploaded_file.name)

        st.session_state.uploaded_files.append(uploaded_file.name)
        return True
    except Exception as exc:
        st.error(f"Failed to process {uploaded_file.name}: {exc}")
        with st.expander("Show full error traceback"):
            st.code(traceback.format_exc(), language="python")
        return False
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _query_rag_engine(question: str, engine: RAGEngine) -> dict:
    try:
        result = engine.get_response(question)
        if isinstance(result, dict):
            answer = result.get("answer", str(result))
            if result.get("is_tool") or result.get("source") == "tool":
                source = "tool"
            else:
                source = "rag" if result.get("is_rag", False) else "llm"
            contexts = result.get("chunks", []) or result.get("contexts", [])
        else:
            answer = getattr(result, "answer", str(result))
            if getattr(result, "is_tool", False) or getattr(result, "source", "") == "tool":
                source = "tool"
            else:
                source = "rag" if getattr(result, "is_rag", False) else "llm"
            contexts = getattr(result, "chunks", []) or getattr(result, "contexts", [])

        return {
            "answer": answer,
            "source": source,
            "contexts": contexts or [],
        }
    except Exception as exc:
        return {
            "answer": f"An error occurred while generating the answer:\n\n`{exc}`",
            "source": "error",
            "contexts": [],
        }


def _render_source_badge(source: str) -> None:
    if source == "rag":
        st.markdown('<span class="badge-rag">From Your Documents (RAG)</span>', unsafe_allow_html=True)
    elif source == "agent":
        st.markdown('<span class="badge-agent">From Autonomous AI Agent (Tools & Search)</span>', unsafe_allow_html=True)
    elif source == "tool":
        st.markdown('<span class="badge-tool">From Real-time Date & Time Tool</span>', unsafe_allow_html=True)
    elif source == "llm":
        st.markdown('<span class="badge-llm">From LLM General Knowledge</span>', unsafe_allow_html=True)


def _render_contexts(contexts: list) -> None:
    if not contexts:
        return
    with st.expander("View retrieved context snippets", expanded=False):
        for idx, ctx in enumerate(contexts, start=1):
            st.markdown(f'<div class="context-box"><strong>Snippet {idx}</strong><br/>{ctx}</div>', unsafe_allow_html=True)


def _render_tools_used(tools_used: list) -> None:
    if not tools_used:
        return
    with st.expander(f"View Agent Intermediate Steps ({len(tools_used)} tools called)", expanded=True):
        for idx, t in enumerate(tools_used, start=1):
            st.markdown(
                f'<div class="tool-box">'
                f'<strong>Step {idx}: [{t.get("tool", "Tool")}]</strong>'
                f'<br/>Input: <code>{t.get("query", "")}</code>'
                f'<br/>Result: {t.get("result", "")}'
                f'</div>',
                unsafe_allow_html=True
            )


def _clear_knowledge_base() -> None:
    if st.session_state.rag_engine is not None:
        if hasattr(st.session_state.rag_engine, "clear"):
            st.session_state.rag_engine.clear()
        else:
            st.session_state.rag_engine = RAGEngine(groq_api_key=st.session_state.groq_api_key)
    st.session_state.uploaded_files = []
    st.session_state.rag_chat_history = []


# =============================================================================
# 4. SIDEBAR: BRANCH SELECTOR & CONTROLS
# =============================================================================

with st.sidebar:
    st.markdown("## Dual AI System")
    st.caption("RAG Model & Autonomous AI Agent")
    st.markdown("---")

    st.markdown("### Select Feature Branch")
    branch_choice = st.radio(
        "Choose Feature:",
        ["Feature 1: RAG Model", "Feature 2: AI Agent"],
        index=0 if st.session_state.active_branch == "rag" else 1,
        help="Switch between Document Retrieval (RAG) and Autonomous Multi-Tool Agent"
    )
    
    is_agent = "AI Agent" in branch_choice
    st.session_state.active_branch = "agent" if is_agent else "rag"

    st.markdown("---")

    st.markdown("### API Configuration")
    groq_input = st.text_input(
        "Groq API Key",
        value=st.session_state.groq_api_key,
        type="password",
        placeholder="gsk_...",
        help="Loaded automatically from .env (Active working key from AI agent)."
    )
    if groq_input and groq_input.strip() != st.session_state.groq_api_key:
        st.session_state.groq_api_key = groq_input.strip()

    tavily_input = st.text_input(
        "Tavily API Key (for Live Web Search)",
        value=st.session_state.tavily_api_key,
        type="password",
        placeholder="tvly-...",
        help="Used by the AI Agent for real-time live internet searches."
    )
    if tavily_input and tavily_input.strip() != st.session_state.tavily_api_key:
        st.session_state.tavily_api_key = tavily_input.strip()

    if groq_input and groq_input.strip():
        st.caption("Groq API Key active")
    if tavily_input and tavily_input.strip():
        st.caption("Tavily Web Search Key active")

    st.markdown("---")

    if not is_agent:
        st.markdown("### Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a PDF or image file",
            type=["pdf", "png", "jpg", "jpeg", "txt"],
            help="Supported formats: PDF, PNG, JPG, JPEG, TXT",
        )

        upload_clicked = st.button("Upload & Process", use_container_width=True, type="primary")

        if upload_clicked:
            if not groq_input or not groq_input.strip():
                st.warning("Please enter your Groq API key before uploading.")
            elif uploaded_file is None:
                st.warning("Please select a file to upload.")
            else:
                engine = _initialise_rag_engine(groq_input.strip())
                with st.spinner(f"Processing {uploaded_file.name} ..."):
                    success = _process_uploaded_file(uploaded_file, engine)
                if success:
                    st.success(f"{uploaded_file.name} added to knowledge base!")

        st.markdown("### Knowledge Base Status")
        num_docs = len(st.session_state.uploaded_files)
        if num_docs == 0:
            st.info("No documents loaded yet.")
        else:
            st.metric(label="Documents Loaded", value=num_docs)
            with st.expander("View loaded files"):
                for fname in st.session_state.uploaded_files:
                    st.markdown(f"- `{fname}`")

        st.markdown("---")
        if st.button("Clear Knowledge Base", use_container_width=True):
            _clear_knowledge_base()
            st.success("Knowledge base cleared.")
            st.rerun()

    else:
        st.markdown("### Active Agent Tools")
        st.markdown(
            """
            - **Wikipedia Search** - Encyclopedic knowledge
            - **Tavily Web Search** - Real-time live web & news
            - **Add Tool** - Exact arithmetic addition
            - **Multiply Tool** - Exact arithmetic multiplication
            - **Autonomous Decision** - Groq `openai/gpt-oss-20b`
            """
        )
        st.markdown("---")
        st.markdown("### Quick Test Prompts")
        if st.button("Alan Turing Biography", use_container_width=True):
            st.session_state.pending_agent_query = "According to Wikipedia, who was Alan Turing and what was his major contribution?"
        if st.button("Math: (452 * 78) + 982", use_container_width=True):
            st.session_state.pending_agent_query = "What is (452 * 78) + 982? Calculate the exact value using your calculation tools."
        if st.button("NASA Artemis News", use_container_width=True):
            st.session_state.pending_agent_query = "Search the live web and tell me the latest news on NASA Artemis missions."

        st.markdown("---")
        if st.button("Clear Agent Chat", use_container_width=True):
            st.session_state.agent_chat_history = []
            st.rerun()


# =============================================================================
# 5. MAIN AREA
# =============================================================================

if not is_agent:
    st.title("Feature 1: RAG Model - Document Q&A")
    st.caption("Upload documents to query them with zero-hallucination vector retrieval.")

    with st.expander("How RAG Works", expanded=False):
        st.markdown(
            """
            Retrieval-Augmented Generation (RAG) indexes your documents into embeddings 
            stored in a FAISS vector index. When you ask a question, the most relevant passages 
            are retrieved and supplied as grounded context to the LLM.
            """
        )

    st.markdown("---")

    for msg in st.session_state.rag_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _render_source_badge(msg.get("source", ""))
                _render_contexts(msg.get("contexts", []))

    user_rag_question = st.chat_input("Ask a question about your documents (or try 'date +2')...")

    if user_rag_question:
        if not groq_input or not groq_input.strip():
            st.error("Please enter your Groq API key in the sidebar first.")
        else:
            engine = _initialise_rag_engine(groq_input.strip())
            st.session_state.rag_chat_history.append({"role": "user", "content": user_rag_question})
            with st.chat_message("user"):
                st.markdown(user_rag_question)

            with st.chat_message("assistant"):
                with st.spinner("Searching documents & thinking..."):
                    result = _query_rag_engine(user_rag_question, engine)
                st.markdown(result["answer"])
                _render_source_badge(result["source"])
                _render_contexts(result["contexts"])

            st.session_state.rag_chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "source": result["source"],
                "contexts": result["contexts"],
            })

    if not st.session_state.rag_chat_history:
        st.markdown(
            """
            <div style="text-align:center; padding:50px 20px; color:#888;">
                <h3>Welcome to RAG Model</h3>
                <p>Upload a PDF or image in the sidebar, or ask general questions / date math below.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    st.title("Feature 2: AI Agent - Autonomous Multi-Tool System")
    st.caption("Equipped with Wikipedia, Tavily Live Web Search, and exact Math tools.")

    with st.expander("How the AI Agent Works", expanded=False):
        st.markdown(
            """
            The AI Agent uses LangChain tool-calling on Groq `openai/gpt-oss-20b` to reason about 
            your question, autonomously invoke tools (Wikipedia, Tavily Search, Add, Multiply), 
            observe their results, and synthesize a comprehensive answer.
            """
        )

    st.markdown("---")

    for msg in st.session_state.agent_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _render_source_badge(msg.get("source", ""))
                _render_tools_used(msg.get("tools_used", []))

    pending_query = st.session_state.pop("pending_agent_query", None)
    user_agent_question = st.chat_input("Ask the AI Agent (e.g., 'Who was Alan Turing?', 'calculate (452 * 78) + 982')...") or pending_query

    if user_agent_question:
        if not groq_input or not groq_input.strip():
            st.error("Please enter your Groq API key in the sidebar first.")
        else:
            agent_exec = _initialise_agent_executor(groq_input.strip(), tavily_input.strip())
            st.session_state.agent_chat_history.append({"role": "user", "content": user_agent_question})
            with st.chat_message("user"):
                st.markdown(user_agent_question)

            with st.chat_message("assistant"):
                with st.spinner("AI Agent thinking & invoking tools..."):
                    result = agent_engine.run_agent_query(agent_exec, user_agent_question)
                st.markdown(result["answer"])
                _render_source_badge(result["source"])
                _render_tools_used(result["tools_used"])

            st.session_state.agent_chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "source": result["source"],
                "tools_used": result["tools_used"],
            })

    if not st.session_state.agent_chat_history:
        st.markdown(
            """
            <div style="text-align:center; padding:50px 20px; color:#888;">
                <h3>Welcome to the AI Agent</h3>
                <p>Ask any complex query, calculation, or recent event. The agent will autonomously pick and execute the right tools.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    f"Dual AI Architecture: RAG Model + AI Agent  |  Groq Model: {os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')}  |  "
    f"Current Branch: {'AI Agent' if is_agent else 'RAG Model'}"
)
