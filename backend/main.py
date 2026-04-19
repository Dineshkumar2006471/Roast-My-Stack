from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from dotenv import load_dotenv
import os
import logging
import httpx
import asyncio
from urllib.parse import urlparse

load_dotenv()

# ── Google Cloud Logging ────────────────────────────────────────────────────
try:
    import google.cloud.logging
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("RoastMyStack backend started — Assistant Personality active")
except Exception:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("RoastMyStack backend started — local logging")

from roast import generate_roast, RoastResponse
roast_code_or_repo = generate_roast
from github_fetch import parse_github_url, fetch_github_code
from context_engine import build_code_context, Language

app = FastAPI(title="RoastMyStack API")

# Configure CORS for frontend access
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS] if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RoastRequest(BaseModel):
    # Support both old and new payload formats for compatibility
    source_type: str = Field(description="Either 'github' or 'snippet'")
    content: str = Field(description="GitHub URL or raw code snippet")
    intensity: str = Field(description="One of: junior, senior, staff")
    
    # New fields for alignment script (optional for backward compatibility)
    code_snippet: Optional[str] = None
    github_url: Optional[str] = None

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: str) -> str:
        if v not in ("junior", "senior", "staff"):
            raise ValueError("intensity must be one of: junior, senior, staff")
        return v

@app.get("/health")
async def health_check():
    return {"status": "ok", "assistant": "active"}

@app.post("/api/roast", response_model=RoastResponse)
async def roast_code(payload: RoastRequest):
    # Resolve code from various possible payload fields
    code = payload.code_snippet or ""
    url = payload.github_url

    # Fallback to old format
    if not code and not url:
        if payload.source_type == "snippet":
            code = payload.content
        elif payload.source_type == "github":
            url = payload.content

    if url:
        try:
            parse_github_url(url)
            code = await fetch_github_code(url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    if not code or len(code.strip()) < 20:
        raise HTTPException(status_code=400, detail="No valid code provided for analysis")

    if len(code) > 500000:
        raise HTTPException(status_code=413, detail="Code too large (max 500KB)")

    # Log the detected context for observability — CRITICAL for PromptWars alignment
    context = build_code_context(code, payload.intensity)
    logger.info(f"Roast request: lang={context.language.value}, "
                f"complexity={context.complexity_score}, "
                f"intensity={context.intensity.value}, "
                f"lines={context.line_count}")

    try:
        result = generate_roast(code, payload.intensity)
        logger.info("Roast generated successfully by the Relentless Senior Engineer")
        
        # Add metadata for shareable URLs or history if needed
        # (This is where save_roast_session logic would go if integrated)
        
        return result
    except Exception as e:
        logger.error(f"Roast generation failed: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail="The assistant encountered an error while reviewing your code.")
