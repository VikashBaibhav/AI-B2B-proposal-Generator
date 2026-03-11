"""
FastAPI Application Entry Point

Wires together all layers of the Clean Architecture:
  - Configures middleware (CORS)
  - Registers routers
  - Sets up lifecycle events
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env BEFORE any other imports that read env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import proposals
from logger.prompt_logger import PromptLogger

logger = PromptLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    import logging
    log = logging.getLogger("main")
    log.info("🚀 AI B2B Proposal Generator API starting up...")
    yield
    log.info("🛑 API shutting down.")


app = FastAPI(
    title="AI B2B Proposal Generator",
    description=(
        "Generate professional, AI-powered B2B sales proposals tailored to each client. "
        "Built with Clean Architecture — domain logic is fully decoupled from AI and DB layers."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow the React frontend dev server during development
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(proposals.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Health check endpoint")
async def health() -> dict:
    return {"status": "ok", "service": "AI B2B Proposal Generator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
