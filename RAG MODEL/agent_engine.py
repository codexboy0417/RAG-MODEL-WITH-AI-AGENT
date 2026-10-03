"""
=============================================================================
AI Agent Engine: Autonomous Multi-Tool Agent with LangChain & Groq
=============================================================================
This module encapsulates the autonomous AI Agent feature:
- Wikipedia Search
- Tavily Live Web Search
- Exact arithmetic (Add, Multiply)
- AgentExecutor with tool tracing and intermediate step tracking
=============================================================================
"""

import os
import sys
import warnings
from typing import Dict, Any, List

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
import wikipedia

try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# User-Agent for Wikipedia API compliance
wikipedia.set_user_agent("PixelCoreAIAgent/1.0 (contact@example.com)")


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
        print(f"Warning: Tavily tool initialization skipped: {e}")
        return None


def build_agent(groq_key: str, tavily_key: str = None, model_name: str = "openai/gpt-oss-20b"):
    """Initializes Groq LLM, tools, prompt, and builds AgentExecutor."""
    llm = ChatGroq(
        model=model_name,
        temperature=0.0,
        api_key=groq_key
    )

    tools = [wikipedia_search, add, multiply]
    has_tavily = False
    if tavily_key and not tavily_key.startswith("YOUR_"):
        tavily_tool = get_tavily_tool(tavily_key)
        if tavily_tool:
            tools.insert(1, tavily_tool)
            has_tavily = True

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

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )
    return executor, tools, llm


def run_agent_query(agent_executor: AgentExecutor, user_input: str) -> Dict[str, Any]:
    """Executes the agent and returns parsed response with tools used."""
    try:
        result = agent_executor.invoke({"input": user_input})
    except Exception as err:
        return {
            "answer": f"Error during agent execution: {err}",
            "tools_used": [],
            "source": "error"
        }

    tools_used = []
    intermediate_steps = result.get("intermediate_steps", [])
    for action, obs in intermediate_steps:
        tool_name = getattr(action, "tool", str(action))
        tool_input = getattr(action, "tool_input", "")
        
        friendly_name = tool_name
        if tool_name == "wikipedia_search":
            friendly_name = "Wikipedia Search"
        elif tool_name == "tavily_search_results_json":
            friendly_name = "Tavily Web Search"
        elif tool_name == "add":
            friendly_name = "Add"
        elif tool_name == "multiply":
            friendly_name = "Multiply"

        tools_used.append({
            "tool": friendly_name,
            "query": str(tool_input),
            "result": str(obs)[:250] + ("..." if len(str(obs)) > 250 else "")
        })

    return {
        "answer": result.get("output", "No output returned."),
        "tools_used": tools_used,
        "source": "agent"
    }
