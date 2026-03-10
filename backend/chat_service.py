import os
from typing import AsyncGenerator
from openai import AsyncOpenAI
from dotenv import load_dotenv
import memory_store

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")


async def get_chat_response(session_id: str, user_message: str, model: str = None) -> tuple[str, str]:
    """
    Get a full (non-streaming) response from OpenAI.
    Returns (reply_text, model_used).
    """
    selected_model = model or DEFAULT_MODEL

    # Add user message to memory
    memory_store.add_message(session_id, "user", user_message)

    # Build message list (includes system prompt)
    messages = memory_store.get_messages_for_api(session_id)

    response = await client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )

    reply = response.choices[0].message.content.strip()

    # Persist assistant reply
    memory_store.add_message(session_id, "assistant", reply)

    return reply, selected_model


async def stream_chat_response(
    session_id: str, user_message: str, model: str = None
) -> AsyncGenerator[str, None]:
    """
    Stream a response from OpenAI token-by-token.
    Saves the full reply to memory after the stream completes.
    """
    selected_model = model or DEFAULT_MODEL

    # Add user message to memory before streaming
    memory_store.add_message(session_id, "user", user_message)

    messages = memory_store.get_messages_for_api(session_id)

    full_reply = ""

    stream = await client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            full_reply += delta
            yield delta

    # Persist complete reply after streaming finishes
    if full_reply:
        memory_store.add_message(session_id, "assistant", full_reply)
