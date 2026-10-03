# -*- coding: utf-8 -*-
"""Copy of AI Agent.py

Converted from Colab Notebook: AI Agent with LangChain & Groq
Practical Implementation: Tools, Wikipedia, Tavily Web Search & Function Calling

#  AI Agents with LangChain & Groq
### Practical Implementation: Tools, Wikipedia, Tavily Web Search & Function Calling
---

##  What is an AI Agent?

An **AI Agent** is a Large Language Model (LLM) that can:
-  **Think** — reason about what needs to be done
-  **Use Tools** — call functions like search, calculator, APIs
-  **Observe** — look at tool results and decide next steps
-  **Repeat** — keep going until the task is done

```
User Question
     │
     ▼
  [THINK]     ← LLM decides what tool to call
     │
     ▼
  [CALL TOOL] ← Wikipedia / Tavily / add / multiply
     │
     ▼
  [OBSERVE]   ← Read tool result
     │
     ▼
 Done? ──No──► [THINK] again
     │Yes
     ▼
 Final Answer
```

##  Tools in This Script

| Tool | Purpose | Source |
|---|---|---|
| `wikipedia_search` | Search Wikipedia for factual & encyclopedic info | `wikipedia` library + `@tool` decorator |
| `tavily_search_results_json` | Search the live web for recent news & real-time info | `langchain_community` / `langchain_tavily` |
| `add` | Custom tool: adds two numbers | `@tool` decorator |
| `multiply` | Custom tool: multiplies two numbers | `@tool` decorator |
| `ChatGroq` | Fast LLM via Groq API | `langchain_groq` |

---
"""

import os
import sys
import getpass
import warnings
from dotenv import load_dotenv

# Ensure standard streams handle UTF-8 / emojis properly on Windows console
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Suppress deprecation warnings for cleaner, readable terminal output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
try:
    from langchain_core._api import LangChainDeprecationWarning
    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
except ImportError:
    pass

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
import wikipedia

# Import Agent components compatible with LangChain v0.3 / v1.0 / classic
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# Set User-Agent for Wikipedia API compliance
wikipedia.set_user_agent("AIAgentTutorial/1.0 (contact@example.com)")


# =====================================================================
#  Step 0: Dependencies
# =====================================================================
# To install all required packages, run in your terminal:
# pip install -r requirements.txt
# (or: pip install langchain langchain-groq langchain-community langchain-classic wikipedia tavily-python python-dotenv)


# =====================================================================
#  Step 3: Create Custom Tools with @tool Decorator
# =====================================================================
@tool
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of a and b.
    """
    return a * b


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information, encyclopedic knowledge, biographies, and historical events.

    Args:
        query: The search term or topic to look up on Wikipedia.

    Returns:
        Summary text from Wikipedia.
    """
    try:
        results = wikipedia.search(query, results=3)
        if not results:
            return f"No Wikipedia pages found for '{query}'."
        page = wikipedia.page(results[0], auto_suggest=False)
        return f"Title: {page.title}\nSummary: {page.summary[:1500]}"
    except wikipedia.DisambiguationError as e:
        if e.options:
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                return f"Title: {page.title}\nSummary: {page.summary[:1500]}"
            except Exception:
                return f"Multiple matches found for '{query}': {', '.join(e.options[:5])}"
        return f"Disambiguation error for '{query}'."
    except wikipedia.PageError:
        return f"No Wikipedia page could be found matching '{query}'."
    except Exception as e:
        return f"Error querying Wikipedia: {e}"


# =====================================================================
#  Step 4: Configure Tavily Web Search Tool
# =====================================================================
def get_tavily_tool(tavily_api_key: str = None):
    """Initializes TavilySearchResults tool if key is present."""
    if not tavily_api_key:
        return None
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        return TavilySearchResults(
            max_results=3,
            description="Search the live web for recent events, breaking news, real-time data, and up-to-date information.",
            tavily_api_key=tavily_api_key
        )
    except Exception as e:
        print(f"  Could not initialize Tavily Search tool: {e}")
        return None


# =====================================================================
#  Step 2 & 5: Construct Agent with Tool Tracking
# =====================================================================
def build_agent(groq_key: str, tavily_key: str = None, model_name: str = "openai/gpt-oss-20b"):
    """Initializes Groq LLM, tools, prompt, and builds AgentExecutor.

    Note: We default to 'openai/gpt-oss-20b' on Groq.
    """
    # 1. Initialize LLM
    llm = ChatGroq(
        model=model_name,
        temperature=0.0,
        api_key=groq_key
    )

    # 2. Build list of available tools
    tools = [wikipedia_search, add, multiply]
    has_tavily = False
    if tavily_key and not tavily_key.startswith("YOUR_"):
        tavily_tool = get_tavily_tool(tavily_key)
        if tavily_tool:
            tools.insert(1, tavily_tool)
            has_tavily = True

    # 3. System Prompt
    tool_descriptions = [
        "1. 'wikipedia_search' - for encyclopedic, historical, and conceptual knowledge from Wikipedia.",
        "2. 'add' - for adding two numbers precisely.",
        "3. 'multiply' - for multiplying two numbers precisely."
    ]
    if has_tavily:
        tool_descriptions.insert(1, "2. 'tavily_search_results_json' - for live, real-time web searches and current news.")

    system_instructions = (
        "You are a helpful, intelligent AI assistant equipped with specialized tools.\n"
        "You have access to:\n"
        + "\n".join(tool_descriptions)
        + "\n\nAlways choose the most appropriate tool for each sub-task. "
        "For arithmetic or calculations, always use the 'add' or 'multiply' tools rather than doing mental math. "
        "Output your final answers in clean, normal, easy-to-read plain text. "
        "Avoid markdown tables, markdown formatting symbols, and excessive hashes."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Create tool-calling agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    # 5. Create executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )
    return executor, tools, llm


def ask_agent(agent_executor: AgentExecutor, user_input: str):
    """Runner function that displays tools used + normal plain text output."""
    try:
        result = agent_executor.invoke({"input": user_input})
    except Exception as err:
        print(f"\n Execution Error: {err}\n")
        return

    print("\n" + "=" * 60)
    print("USER QUERY:", user_input)
    print("-" * 60)

    # Check and print tools used
    intermediate_steps = result.get("intermediate_steps", [])
    if intermediate_steps:
        print("  TOOLS USED:")
        for action, _ in intermediate_steps:
            tool_name = getattr(action, "tool", str(action))
            tool_input = getattr(action, "tool_input", "")
            if tool_name == "wikipedia_search":
                print(f"  • Tool: [Wikipedia] -> Query: {tool_input}")
            elif tool_name == "tavily_search_results_json":
                print(f"  • Tool: [Tavily Web Search] -> Query: {tool_input}")
            elif tool_name == "add":
                print(f"  • Tool: [Add] -> Adding: {tool_input}")
            elif tool_name == "multiply":
                print(f"  • Tool: [Multiply] -> Multiplying: {tool_input}")
            else:
                print(f"  • Tool: [{tool_name}] -> Input: {tool_input}")
    else:
        print("  TOOLS USED: None (Direct Answer)")

    print("-" * 60)
    print(" OUTPUT:")
    print(result.get("output", "No output returned."))
    print("=" * 60 + "\n")


# =====================================================================
#  Step 6: Testing Agent Capabilities
# =====================================================================
def run_tests(agent_executor: AgentExecutor, has_tavily: bool = False):
    """Runs test queries to demonstrate tool usage."""
    print("\n" + "=" * 60)
    print(" Running Agent Demonstration Tests")
    print("=" * 60)

    print("\n--- Test 1: Wikipedia Search ---")
    ask_agent(agent_executor, "According to Wikipedia, who was Alan Turing and what was his major contribution?")

    print("\n--- Test 2: Custom Math Tools (add & multiply) ---")
    ask_agent(agent_executor, "What is (452 * 78) + 982? Calculate the exact value using your calculation tools.")

    if has_tavily:
        print("\n--- Test 3: Live Web Search with Tavily ---")
        ask_agent(agent_executor, "Search the web and tell me the latest news on NASA Artemis missions.")

        print("\n--- Test 4: Multi-Tool Reasoning (Search + Math) ---")
        ask_agent(agent_executor, "Find the approximate population of Tokyo and Paris from search/Wikipedia, and calculate their combined total sum with your math tools.")
    else:
        print("\n--- Test 3: Multi-Tool Reasoning (Wikipedia + Math) ---")
        ask_agent(agent_executor, "According to Wikipedia, what are the years of birth and death of Isaac Newton, and calculate how old he was when he died using your calculation tools.")


# =====================================================================
#  Step 7: Interactive Chat Loop & Main Entry Point
# =====================================================================
def main():
    # Load from .env file if present
    load_dotenv()

    # Retrieve Groq API Key
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    is_placeholder_groq = not groq_key or groq_key.startswith("YOUR_")

    if is_placeholder_groq:
        if sys.stdin.isatty():
            print("Please enter your active Groq API Key (starts with gsk_):")
            user_input_key = getpass.getpass("Groq API Key: ").strip()
            if user_input_key:
                groq_key = user_input_key
                os.environ["GROQ_API_KEY"] = groq_key
        else:
            print("  Warning: GROQ_API_KEY is not set or is a placeholder in .env / environment.")

    # Retrieve Tavily API Key
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key.startswith("YOUR_"):
        # Placeholder detected, ignore it
        tavily_key = ""

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    print("\n--- API Configuration ---")
    print("Groq API Key:  ", " Ready" if groq_key and not groq_key.startswith("YOUR_") else " Missing / Placeholder")
    print("Tavily API Key:", " Ready" if tavily_key else "  Not configured (Web search disabled, Wikipedia & Math active)")
    print(f"Model:          {model_name}\n")

    if not groq_key or groq_key.startswith("YOUR_"):
        print(" Cannot proceed without a valid Groq API Key.")
        print(" Please get a free API key at: https://console.groq.com/keys")
        print(" Add it to a .env file: GROQ_API_KEY=your_key_here\n")
        return

    # Build agent
    print(" Initializing Groq AI Agent...")
    try:
        agent_executor, tools, llm = build_agent(groq_key, tavily_key, model_name)
    except Exception as e:
        print(f" Failed to initialize Agent: {e}")
        return

    # Test LLM connection
    try:
        test_response = llm.invoke("Explain what an AI Agent is in one sentence.")
        print(" LLM Connection Test:", test_response.content.strip())
    except Exception as e:
        print(f" LLM Connection Test Failed: {e}")
        print("Please verify that your Groq API key is valid and has active quota.")
        return

    print(f" Loaded {len(tools)} tools: {[t.name for t in tools]}")
    print(" AI Agent is ready!\n")

    # Command line argument handling: python copy_of_ai_agent.py --test
    if "--test" in sys.argv:
        run_tests(agent_executor, has_tavily=bool(tavily_key))
        return

    # Interactive session prompt
    print("=" * 60)
    print(" AI Agent Interactive Chat Session")
    print("Type your question below.")
    print("Type 'run tests' to execute sample tests, or 'exit' / 'quit' to end.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n Goodbye!")
            break
        if user_input.lower() in ["run tests", "test", "tests"]:
            run_tests(agent_executor, has_tavily=bool(tavily_key))
            continue

        ask_agent(agent_executor, user_input)


if __name__ == "__main__":
    main()