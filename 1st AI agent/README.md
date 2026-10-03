# Autonomous AI Agent with LangChain and Groq

Practical implementation of an autonomous AI agent equipped with Wikipedia search, Tavily web search, and custom mathematical tools (`add` and `multiply`) using Groq's high-speed Language Processing Unit inference.

---

## 1. Quick Start

### 1.1 Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Set your keys inside `.env`:
- **`GROQ_API_KEY`** (Required): Obtain from [Groq Console](https://console.groq.com/keys).
- **`TAVILY_API_KEY`** (Optional): Obtain from [Tavily](https://app.tavily.com). *If omitted, the agent automatically executes with Wikipedia and Math tools.*

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.3 Run the Agent
To start an interactive terminal session:
```bash
python copy_of_ai_agent.py
```

To run automated capability tests:
```bash
python copy_of_ai_agent.py --test
```

---

## 2. Available Tools

| Tool Identifier | Functional Purpose | Execution Status |
|---|---|---|
| `wikipedia_search` | Queries MediaWiki Wikipedia APIs for encyclopedic facts and summaries | Always enabled |
| `add` | Sandboxed floating-point addition engine | Always enabled |
| `multiply` | Sandboxed floating-point multiplication engine | Always enabled |
| `tavily_search_results_json` | Live internet search for recent events and current information | Enabled when `TAVILY_API_KEY` is present |

---

## 3. Architecture Summary
The agent utilizes LangChain's `create_tool_calling_agent` pattern coupled with `AgentExecutor`. The LLM evaluates user intent, binds functions dynamically, calls tools synchronously, observes outputs, and synthesizes a final plain-text answer without markdown formatting artifacts.
