from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

from roast import roast_code_or_repo, RoastResponse

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
    source_type: str  # "github" or "snippet"
    content: str      # URL or raw code
    intensity: str    # "junior", "senior", "staff"

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/roast", response_model=RoastResponse)
async def create_roast(request: RoastRequest):
    try:
        if request.source_type not in ["github", "snippet"]:
            raise HTTPException(status_code=400, detail="Invalid source_type. Must be 'github' or 'snippet'.")
        if request.intensity not in ["junior", "senior", "staff"]:
            raise HTTPException(status_code=400, detail="Invalid intensity. Must be 'junior', 'senior', or 'staff'.")
        
        result = await roast_code_or_repo(request.source_type, request.content, request.intensity)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
