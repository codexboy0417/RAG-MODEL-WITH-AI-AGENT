# Dual AI Engine: RAG Model and Autonomous AI Agent

A unified, dual-branch artificial intelligence platform combining Retrieval-Augmented Generation (Document Q&A) and an Autonomous Multi-Tool AI Agent into a single web interface.

---

## Overview

This repository provides two core capabilities selectable from a unified web interface:

1. **Feature 1: RAG Model (Document Q&A)**
   - Upload and parse PDFs, images (via OCR), and text documents.
   - Text chunking with overlapping windows and vector indexing using FAISS.
   - Source-attributed answers with expandable context snippets (grounded retrieval with zero hallucination).
   - Deterministic real-time date calculator (relative offsets such as 'date +2' and '10 days before').

2. **Feature 2: Autonomous AI Agent**
   - Autonomous tool-calling engine powered by Groq (openai/gpt-oss-20b).
   - Wikipedia Search: Encyclopedic knowledge, history, and biographies.
   - Tavily Live Web Search: Real-time news and current internet data.
   - Arithmetic Tools: Exact addition and multiplication to prevent math hallucinations.
   - Transparent intermediate step tracking and tool observation logs.

---

## Project Structure

```
RAG MODEL WITH AI AGENT/
├── 1st AI agent/                   # Standalone AI agent prototype
│   ├── copy_of_ai_agent.py
│   ├── requirements.txt
│   └── README.md
│
├── RAG MODEL/                      # Integrated Dual-Engine Application
│   ├── frontend/                   # React + Vite + Tailwind interactive UI
│   │   ├── src/components/
│   │   │   ├── Header.jsx          # Top navigation with branch switcher
│   │   │   ├── HeroTablet.jsx      # Hero section with dual-branch controls
│   │   │   ├── InteractivePlayground.jsx # Studio with live dual-engine chat
│   │   │   └── ApiKeyModal.jsx     # API configuration modal
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   ├── app.py                      # Streamlit application with dual branches
│   ├── rag_engine.py               # Core RAG retrieval and vector store engine
│   ├── agent_engine.py             # LangChain tool-calling AI Agent module
│   ├── tools.py                    # Real-time calculation tools
│   ├── demo_dual.py                # Command-line dual-branch test script
│   ├── HOW_TO_RUN_PROJECT.txt      # Comprehensive execution guide
│   ├── RUN_FRONTEND.bat            # 1-click launcher for React UI
│   └── RUN_STREAMLIT.bat           # 1-click launcher for Streamlit
│
├── .gitignore                      # Git ignore rules (protects .env secrets)
└── README.md                       # This file
```

---

## Quick Start

### Prerequisites
- Node.js (v18 or higher)
- Python (3.8 or higher)
- Groq API Key (https://console.groq.com/keys)
- Tavily API Key (Optional for web search: https://app.tavily.com)

### Setup Environment
1. Copy the environment template:
   ```bash
   cd "RAG MODEL"
   copy .env.example .env
   ```
2. Enter your API keys in `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   GROQ_MODEL=openai/gpt-oss-20b
   ```

### Run Option 1: Interactive Web App (Recommended)
```bash
cd "RAG MODEL/frontend"
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### Run Option 2: Streamlit Dashboard
```bash
cd "RAG MODEL"
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Run Option 3: Terminal CLI Demo
```bash
cd "RAG MODEL"
python demo_dual.py
```

---

## License
MIT License. Open source and free to use.
