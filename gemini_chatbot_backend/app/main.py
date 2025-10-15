import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables from .env if present
load_dotenv()

GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

app = FastAPI(
    title="Gemini Chatbot Backend",
    description="Minimal FastAPI backend that proxies chat requests to Google Gemini and returns the response.",
    version="0.1.0",
    contact={"name": "Chatbot Backend"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "health", "description": "Health and status endpoints"},
        {"name": "chat", "description": "Chat with Gemini"},
    ],
)

# Restrict CORS to the frontend URL(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://vscode-internal-33666-beta.beta01.cloud.kavia.ai:3000",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class ChatRequest(BaseModel):
    # PUBLIC_INTERFACE
    message: str = Field(..., description="The user's input message to send to Gemini")


class ChatResponse(BaseModel):
    # PUBLIC_INTERFACE
    reply: str = Field(..., description="The model's reply text")


class ErrorResponse(BaseModel):
    # PUBLIC_INTERFACE
    error: str = Field(..., description="Error message")


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint that returns a simple status message."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/chat",
    tags=["chat"],
    summary="Chat GET helper",
)
def chat_get_info():
    """
    Provide usage info for the chat endpoint.

    Returns:
    - JSON object with a short instruction message for clients to use POST /chat.
    """
    return {"message": "Use POST /chat with JSON payload { 'message': '...'} to chat."}


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["chat"],
    summary="Send a message to Gemini",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    PUBLIC_INTERFACE
    Handle a chat message by proxying it to Google Gemini (if configured) or returning an echo reply.

    Parameters:
    - request: ChatRequest
      The chat request containing a 'message' field.

    Returns:
    - ChatResponse
      A JSON object with a single 'reply' field which contains the model's response text.

    Behavior:
    - If GEMINI_API_KEY is not configured, returns an echo reply to ensure a successful 200 response for development.
    - If GEMINI_API_KEY is configured, proxies the request to Gemini and returns the model's reply.

    Error responses:
    - 400 with {'error': string} when request is invalid
    - 500 with {'error': string} for upstream or unexpected errors
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Development-friendly fallback if GEMINI_API_KEY isn't set:
    if not GEMINI_API_KEY:
        return ChatResponse(reply=f"Echo: {request.message}")

    # Build Gemini REST payload (generateContent)
    payload = {
        "contents": [{"parts": [{"text": request.message}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 512,
        },
    }

    params = {"key": GEMINI_API_KEY}
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(GEMINI_API_URL, params=params, json=payload, headers=headers)
            if resp.status_code >= 400:
                # Attempt to extract error message from Gemini response
                err_text = "Upstream error from Gemini"
                try:
                    data = resp.json()
                    if isinstance(data, dict):
                        # Common error structures
                        if "error" in data and isinstance(data["error"], dict):
                            err_text = data["error"].get("message") or err_text
                        elif "message" in data:
                            err_text = data.get("message", err_text)
                except Exception:
                    pass
                raise HTTPException(status_code=500, detail=err_text)

            data = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=500, detail="Request to Gemini timed out")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Network error contacting Gemini: {e}")

    # Parse reply text from Gemini response
    reply_text = ""
    try:
        candidates = data.get("candidates", [])
        if candidates:
            # Gemini generateContent returns candidates[].content.parts[].text
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts and isinstance(parts[0], dict):
                reply_text = parts[0].get("text", "") or ""
        if not reply_text and "text" in data:
            reply_text = data.get("text") or ""
    except Exception:
        reply_text = ""

    if not reply_text:
        raise HTTPException(status_code=500, detail="No reply generated by Gemini")

    return ChatResponse(reply=reply_text)
