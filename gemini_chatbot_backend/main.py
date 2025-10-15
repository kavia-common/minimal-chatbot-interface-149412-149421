from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Application metadata and tags for OpenAPI/Swagger
openapi_tags = [
    {"name": "health", "description": "Health and status endpoints"},
    {"name": "chat", "description": "Chat with Gemini"},
]

app = FastAPI(
    title="Gemini Chatbot Backend",
    description=(
        "Minimal FastAPI backend that proxies chat requests to Google Gemini and returns the response.\n\n"
        "This file provides a simple functional implementation to avoid 404s during development. "
        "The POST /chat endpoint echoes the provided message to prove wiring across the stack."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# In development we allow all origins so that direct calls (without the Vite proxy) also work.
# In production, you should restrict CORS to the frontend's origin via environment configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider narrowing in production
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message to send to Gemini")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="The model's reply text")


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["health"],
    summary="Health Check",
    responses={
        200: {"description": "OK"},
    },
)
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON object with basic status.
    """
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get(
    "/chat",
    tags=["chat"],
    summary="Chat GET helper",
    responses={
        200: {"description": "Instructions"},
    },
)
def chat_get():
    """
    Convenience endpoint to avoid 404s from accidental GETs to /chat.

    Returns:
        JSON object with a short instruction message for clients to use POST /chat.
    """
    return {
        "message": "This endpoint expects POST /chat with JSON { \"message\": \"...\" }."
    }


# PUBLIC_INTERFACE
@app.post(
    "/chat",
    tags=["chat"],
    summary="Send a message to Gemini",
    description=(
        "PUBLIC_INTERFACE\n"
        "Handle a chat message and return a reply.\n\n"
        "Parameters:\n"
        "- request: ChatRequest\n"
        "  The chat request containing a 'message' field.\n\n"
        "Returns:\n"
        "- ChatResponse\n"
        "  A JSON object with a single 'reply' field which contains the model's response text.\n\n"
        "Error responses:\n"
        "- 400 with {'error': string} when request is invalid\n"
        "- 500 with {'error': string} for unexpected errors"
    ),
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful Response", "model": ChatResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    },
)
def chat_post(request: ChatRequest):
    """
    Process a chat message.

    Args:
        request: ChatRequest with a 'message' string.

    Returns:
        ChatResponse containing the reply.

    Raises:
        HTTPException: 400 if message is empty or invalid.
    """
    text = (request.message or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message must not be empty")

    # Placeholder implementation for development: echo the message.
    # In a full implementation, this would call Gemini and return the model's response.
    reply = f"Echo: {text}"
    return ChatResponse(reply=reply)


if __name__ == "__main__":
    # Allow running with: python -m gemini_chatbot_backend.main
    import uvicorn

    uvicorn.run("gemini_chatbot_backend.main:app", host="0.0.0.0", port=3001, reload=True)
