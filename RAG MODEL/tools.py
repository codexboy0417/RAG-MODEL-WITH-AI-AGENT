"""
=============================================================================
Tools Module: Real-time Date, Time, and Relative Date Calculations
=============================================================================
This module provides real-time tools using the LangChain @tool pattern
(as studied in your Google Colab notebooks).

Tools included:
1. get_current_datetime()      - Current real-time date and time
2. calculate_relative_date()   - Dynamic date math (e.g., 10 days before/after)
3. get_weather()               - Weather mock tool from your Colab study
=============================================================================
"""

import re
import datetime
from typing import Optional, Dict, Any

try:
    from langchain.tools import tool
except ImportError:
    # Lightweight fallback decorator if langchain is not present
    def tool(func):
        func.is_tool = True
        return func


@tool
def get_current_datetime() -> str:
    """
    Returns the exact real-time current date, day of week, and time.
    Use this when the user asks for today's date, current time, or day.
    """
    now = datetime.datetime.now()
    return (
        f" **Current Date**: {now.strftime('%A, %d %B %Y')}\n"
        f" **Current Time**: {now.strftime('%I:%M:%S %p')}\n"
        f" **Timestamp**: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )


@tool
def calculate_relative_date(query: str, days_offset: int = 0) -> str:
    """
    Calculates past or future dates relative to today.
    Example queries handled:
      - '10 days before'
      - '10 days after' / '10 days later'
      - '3 weeks ago'
      - 'yesterday' / 'tomorrow'
    """
    now = datetime.datetime.now()
    q = query.lower()

    # Parse relative day expressions like "10 days before", "5 days ago", etc.
    match_before = re.search(r'(\d+)\s*(days?|weeks?|months?)\s*(before|ago|earlier|prior|back)', q)
    match_after = re.search(r'(\d+)\s*(days?|weeks?|months?)\s*(after|later|from now|ahead)', q)

    if match_before:
        num = int(match_before.group(1))
        unit = match_before.group(2)
        days = num * 7 if 'week' in unit else (num * 30 if 'month' in unit else num)
        target = now - datetime.timedelta(days=days)
        return (
            f" **Today's Reference Date**: {now.strftime('%A, %d %B %Y')}\n"
            f" **Reference Time**: {now.strftime('%I:%M:%S %p')}\n\n"
            f" **Calculated Date ({num} {unit} before)**:\n"
            f"- **Date**: {target.strftime('%A, %d %B %Y')}\n"
            f"- **Time**: {target.strftime('%I:%M:%S %p')}\n"
            f"- **ISO Format**: {target.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    elif match_after:
        num = int(match_after.group(1))
        unit = match_after.group(2)
        days = num * 7 if 'week' in unit else (num * 30 if 'month' in unit else num)
        target = now + datetime.timedelta(days=days)
        return (
            f" **Today's Reference Date**: {now.strftime('%A, %d %B %Y')}\n"
            f" **Reference Time**: {now.strftime('%I:%M:%S %p')}\n\n"
            f" **Calculated Date ({num} {unit} after)**:\n"
            f"- **Date**: {target.strftime('%A, %d %B %Y')}\n"
            f"- **Time**: {target.strftime('%I:%M:%S %p')}\n"
            f"- **ISO Format**: {target.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    elif 'yesterday' in q:
        target = now - datetime.timedelta(days=1)
        return (
            f" **Today**: {now.strftime('%A, %d %B %Y')}\n"
            f" **Yesterday**: {target.strftime('%A, %d %B %Y')}"
        )

    elif 'tomorrow' in q:
        target = now + datetime.timedelta(days=1)
        return (
            f" **Today**: {now.strftime('%A, %d %B %Y')}\n"
            f" **Tomorrow**: {target.strftime('%A, %d %B %Y')}"
        )

    elif days_offset != 0:
        target = now + datetime.timedelta(days=days_offset)
        direction = "ahead" if days_offset > 0 else "prior"
        return (
            f" **Today**: {now.strftime('%A, %d %B %Y')}\n"
            f" **Target Date ({abs(days_offset)} days {direction})**: {target.strftime('%A, %d %B %Y, %I:%M:%S %p')}"
        )

    else:
        return get_current_datetime()


@tool
def get_weather(city: str) -> str:
    """
    Returns current weather for a given city (from your Google Colab example).
    Input should be a city name like 'Delhi', 'Mumbai', 'London'.
    """
    weather_db = {
        "delhi": " Delhi: 34°C, Partly Cloudy, Humidity 45%",
        "mumbai": " Mumbai: 28°C, Light Rain, Humidity 80%",
        "london": " London: 15°C, Overcast, Humidity 70%",
        "new york": " New York: 22°C, Sunny, Humidity 55%",
        "tokyo": " Tokyo: 18°C, Clear, Humidity 60%",
    }
    return weather_db.get(city.lower().strip(), f" No data for '{city}'. Try: Delhi, Mumbai, London, New York, Tokyo")


def handle_datetime_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Detects if a user question is asking about real-time date/time or relative date math.
    Returns structured output if matched, otherwise None.
    """
    q = query.lower()

    # Keywords signaling date or time query
    date_keywords = ["date", "time", "day", "today", "yesterday", "tomorrow", "clock", "now"]
    has_date_keyword = any(kw in q for kw in date_keywords)

    # Patterns for relative calculations (e.g., "10 days before", "5 days ago", etc.)
    has_relative_pattern = bool(
        re.search(r'\d+\s*(days?|weeks?|months?)\s*(before|ago|earlier|prior|after|later|ahead)', q)
    )

    if not has_date_keyword and not has_relative_pattern:
        return None

    # If it is a relative calculation
    if has_relative_pattern or "yesterday" in q or "tomorrow" in q or "before" in q or "after" in q or "ago" in q:
        result_text = calculate_relative_date(query)
        return {
            "answer": result_text,
            "tool_name": "calculate_relative_date",
            "is_tool": True,
            "source_label": " From Real-time Date/Time Tool",
        }

    # Otherwise if asking about today/now/current date/time
    if any(phrase in q for phrase in [
        "what's the date", "what is the date", "whats the date", "todays date", "today's date",
        "current date", "what date is today", "what is today", "what's today",
        "current time", "what time is it", "whats the time", "what is the time", "time now"
    ]):
        result_text = get_current_datetime()
        return {
            "answer": result_text,
            "tool_name": "get_current_datetime",
            "is_tool": True,
            "source_label": " From Real-time Date/Time Tool",
        }

    return None
