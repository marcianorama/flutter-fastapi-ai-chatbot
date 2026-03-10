from typing import Dict, List
from datetime import datetime, timezone


# In-memory store: session_id -> list of message dicts
# Each message: {"role": "user"|"assistant"|"system", "content": str, "timestamp": str}
_sessions: Dict[str, List[dict]] = {}

SYSTEM_PROMPT = """You are an intelligent, helpful, and friendly AI assistant built for a portfolio demonstration. 
You provide accurate, thoughtful, and concise responses. 
When writing code, always use proper formatting with code blocks.
You can help with programming, analysis, creative writing, math, general knowledge, and more.
Be professional yet approachable."""

MAX_HISTORY_TURNS = 10  # Keep last 10 user/assistant pairs


def get_or_create_session(session_id: str) -> List[dict]:
    """Get existing session or create a new one with the system prompt."""
    if session_id not in _sessions:
        _sessions[session_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
                "timestamp": _now(),
            }
        ]
    return _sessions[session_id]


def add_message(session_id: str, role: str, content: str) -> None:
    """Add a message to a session."""
    session = get_or_create_session(session_id)
    session.append({
        "role": role,
        "content": content,
        "timestamp": _now(),
    })
    _trim_session(session_id)


def get_messages_for_api(session_id: str) -> List[dict]:
    """Return messages in the format expected by OpenAI API (role + content only)."""
    session = get_or_create_session(session_id)
    return [{"role": m["role"], "content": m["content"]} for m in session]


def get_messages_for_history(session_id: str) -> List[dict]:
    """Return messages for the /history endpoint (excludes the system prompt)."""
    session = get_or_create_session(session_id)
    return [m for m in session if m["role"] != "system"]


def clear_session(session_id: str) -> None:
    """Clear a session (reset to system prompt only)."""
    _sessions[session_id] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
            "timestamp": _now(),
        }
    ]


def session_exists(session_id: str) -> bool:
    return session_id in _sessions


def _trim_session(session_id: str) -> None:
    """Keep only system prompt + last MAX_HISTORY_TURNS * 2 messages."""
    session = _sessions.get(session_id, [])
    system_msgs = [m for m in session if m["role"] == "system"]
    other_msgs = [m for m in session if m["role"] != "system"]
    max_msgs = MAX_HISTORY_TURNS * 2  # user + assistant pairs
    if len(other_msgs) > max_msgs:
        other_msgs = other_msgs[-max_msgs:]
    _sessions[session_id] = system_msgs + other_msgs


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
