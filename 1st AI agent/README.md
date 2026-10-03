# 🤖 AI Agent with LangChain & Groq

Practical implementation of an autonomous AI agent equipped with Wikipedia search, Tavily web search, and custom mathematical tools (`add` & `multiply`) using Groq's ultra-fast LLM inference.

---

## 🚀 Quick Start

### 1. Configure Your API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and paste your keys:
- **`GROQ_API_KEY`** (Required): Get a free key at [Groq Console](https://console.groq.com/keys).
- **`TAVILY_API_KEY`** (Optional): Get a free key at [Tavily](https://app.tavily.com). *If omitted, the agent automatically runs with Wikipedia and Math tools.*

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Agent
To start an interactive chat session:
```bash
python copy_of_ai_agent.py
```

To run automated capability tests:
```bash
python copy_of_ai_agent.py --test
```
*(You can also type `run tests` inside the interactive session at any time).*

---

## 🛠️ Available Tools

| Tool | Purpose | Status |
|---|---|---|
| `wikipedia_search` | Search Wikipedia for encyclopedic facts and summaries | Always active |
| `add` | Accurate floating point addition | Always active |
| `multiply` | Accurate floating point multiplication | Always active |
| `tavily_search_results_json` | Live internet search for recent events & breaking news | Active when `TAVILY_API_KEY` is provided |
