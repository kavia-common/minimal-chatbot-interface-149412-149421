# Gemini Chatbot Backend (FastAPI)

Minimal FastAPI backend that proxies chat requests to Google Gemini and returns the response.

## Requirements
- Python 3.10+
- Environment variable GEMINI_API_KEY set (see .env.example)

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

## CORS
CORS is configured to allow http://localhost:3000 (the frontend).

## Endpoints

- GET /
  Health check returning {"message": "Healthy"}.

- POST /chat
  Request:
  {
    "message": "Hello"
  }

  Response:
  {
    "reply": "Hi! How can I help you today?"
  }

### Errors
All errors return JSON:
{
  "error": "Message text here"
}

Common issues:
- 400: GEMINI_API_KEY is not configured or message is empty
- 500: Upstream or network errors when contacting Gemini
