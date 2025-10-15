# Gemini Chatbot Backend (FastAPI)

Minimal FastAPI backend that proxies chat requests to Google Gemini and returns the response. If GEMINI_API_KEY is not configured, the backend returns a simple echo reply so POST /chat always works during development.

## Requirements
- Python 3.10+
- Environment variable GEMINI_API_KEY set (see .env.example) for real Gemini responses
- For development without an API key, the service will return an echo reply

## Setup
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   pip install -r requirements.txt
3. Copy .env.example to .env and set GEMINI_API_KEY:
   cp .env.example .env
   # Edit .env to insert your key

## Run
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

The app will be available at:
- API Docs: http://localhost:3001/docs
- OpenAPI: http://localhost:3001/openapi.json

Entrypoint module is app/main.py (there is no alternate main.py at the project root to avoid confusion).

## CORS
CORS is configured to allow these frontend origins:
- http://localhost:3000
- https://vscode-internal-33666-beta.beta01.cloud.kavia.ai:3000

Allowed methods: GET, POST, OPTIONS
Allowed headers: Content-Type, Authorization

## Endpoints

- GET /
  Health check returning {"message": "Healthy"}.

- GET /chat
  Info endpoint with usage instructions for POST /chat.

- POST /chat
  Request:
  {
    "message": "Hello"
  }

  Response (development without GEMINI_API_KEY):
  {
    "reply": "Echo: Hello"
  }

  Response (with GEMINI_API_KEY configured):
  {
    "reply": "Hi! How can I help you today?"
  }

### Errors
All errors return JSON:
{
  "error": "Message text here"
}

Common issues:
- 400: Message is empty
- 500: Upstream or network errors when contacting Gemini (only when GEMINI_API_KEY is set)
