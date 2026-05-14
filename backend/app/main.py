from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models import SearchRequest, SearchResponse
from app.services import llm, search_service
from app.services.http_client import HttpClientManager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize HTTP client
    HttpClientManager.get_client()
    yield
    # Shutdown: Close HTTP client
    await HttpClientManager.close_client()

app = FastAPI(title="InPost Global Search Enrichment", lifespan=lifespan)

# Configure CORS for the frontend - restrictive in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/status")
async def status():
    """Returns the current LLM mode so the frontend can show a notice."""
    return {"llm_mode": "mock" if llm.api_key == "mock-key" else "gemini"}


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return await search_service.execute_search(request)
