from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# ── Google Cloud Logging ────────────────────────────────────────────────────
try:
    import google.cloud.logging
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("RoastMyStack backend started — Cloud Logging active")
except Exception:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("RoastMyStack backend started — local logging (Cloud Logging unavailable)")

from roast import roast_code_or_repo, RoastResponse
from github_fetch import parse_github_url

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

# Maximum code snippet size (500KB)
MAX_CODE_SIZE = 500_000


class RoastRequest(BaseModel):
    source_type: str = Field(description="Either 'github' or 'snippet'")
    content: str = Field(description="GitHub URL or raw code snippet")
    intensity: str = Field(description="One of: junior, senior, staff")

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: str) -> str:
        if v not in ("junior", "senior", "staff"):
            raise ValueError("intensity must be one of: junior, senior, staff")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        if v not in ("github", "snippet"):
            raise ValueError("source_type must be 'github' or 'snippet'")
        return v


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/api/health")
async def api_health_check():
    """API-prefixed health check endpoint."""
    return {"status": "ok"}


@app.post("/api/roast", response_model=RoastResponse)
async def create_roast(request: RoastRequest):
    logger.info(f"Roast request received: source_type={request.source_type}, intensity={request.intensity}")
    try:
        # Validate GitHub URL format
        if request.source_type == "github":
            if "github.com" not in request.content:
                raise HTTPException(status_code=400, detail="Invalid GitHub URL. Must be a github.com URL.")
            try:
                parse_github_url(request.content)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Enforce code size limit
        if request.source_type == "snippet" and len(request.content) > MAX_CODE_SIZE:
            raise HTTPException(status_code=400, detail=f"Code snippet too large. Maximum size is {MAX_CODE_SIZE} characters.")

        result = await roast_code_or_repo(request.source_type, request.content, request.intensity)
        logger.info("Roast generated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error in roast generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Roast generation failed: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
