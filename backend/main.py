import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

import memory_store
import chat_service
from models import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageRecord,
    ClearResponse,
    HealthResponse,
)

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "AI Chatbot API")
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title=APP_NAME,
    description="Production-quality AI Chatbot API — Portfolio Project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow all origins for local development (Flutter emulator uses a different host)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
#  Health Check
# ─────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        model=MODEL,
    )


# ─────────────────────────────────────────────
#  Chat Endpoint (non-streaming, simple JSON)
# ─────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a message and receive a complete AI response.
    Uses in-memory conversation history per session_id.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        reply, model_used = await chat_service.get_chat_response(
            session_id=request.session_id,
            user_message=request.message,
            model=request.model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    return ChatResponse(
        reply=reply,
        session_id=request.session_id,
        model_used=model_used,
    )


# ─────────────────────────────────────────────
#  Chat Stream Endpoint (SSE streaming)
# ─────────────────────────────────────────────

@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    Send a message and receive a streamed AI response (Server-Sent Events).
    Each chunk is a plain text token. Flutter can read these incrementally.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    async def generator():
        try:
            async for chunk in chat_service.stream_chat_response(
                session_id=request.session_id,
                user_message=request.message,
                model=request.model,
            ):
                yield chunk
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return StreamingResponse(generator(), media_type="text/plain")


# ─────────────────────────────────────────────
#  History Endpoint
# ─────────────────────────────────────────────

@app.get("/history/{session_id}", response_model=HistoryResponse, tags=["History"])
async def get_history(session_id: str):
    """
    Retrieve conversation history for a given session.
    System messages are excluded from the response.
    """
    messages = memory_store.get_messages_for_history(session_id)
    return HistoryResponse(
        session_id=session_id,
        messages=[
            MessageRecord(
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"],
            )
            for m in messages
        ],
        total_messages=len(messages),
    )


# ─────────────────────────────────────────────
#  Clear Session Endpoint
# ─────────────────────────────────────────────

@app.delete("/clear/{session_id}", response_model=ClearResponse, tags=["History"])
async def clear_history(session_id: str):
    """
    Clear the conversation history for a given session.
    The system prompt is retained; all user/assistant messages are removed.
    """
    memory_store.clear_session(session_id)
    return ClearResponse(
        session_id=session_id,
        message="Conversation history cleared successfully.",
    )


# ─────────────────────────────────────────────
#  Run directly (for development)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG)
