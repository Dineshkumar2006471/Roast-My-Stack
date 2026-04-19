import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from github_fetch import fetch_github_repo

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

class Issue(BaseModel):
    type: str = Field(description="Type of the issue, e.g., 'Security', 'Performance', 'Naming'")
    line: Optional[int] = Field(None, description="Line number where issue occurs, if applicable")
    description: str = Field(description="Detailed description of what is wrong")
    severity: str = Field(description="Severity (critical/high/medium/low)")

class FixStep(BaseModel):
    issue: str = Field(description="The issue being addressed")
    fix: str = Field(description="Specific actionable fix")
    priority: int = Field(description="Priority number (1 being highest)")

class Scores(BaseModel):
    codeQuality: int = Field(description="Score 0-100")
    security: int = Field(description="Score 0-100")
    efficiency: int = Field(description="Score 0-100")
    testing: int = Field(description="Score 0-100")
    accessibility: int = Field(description="Score 0-100")

class RoastResponse(BaseModel):
    roast: str = Field(description="A brutal, honest roast of the code")
    issues: List[Issue] = Field(description="List of specific issues found")
    fixPlan: List[FixStep] = Field(description="Structured plan to fix the issues")
    scores: Scores = Field(description="Numeric scores evaluating the code")

from context_engine import build_code_context, build_analysis_prompt

async def roast_code_or_repo(source_type: str, content: str, intensity: str) -> dict:
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")
    
    code_text = content
    if source_type == "github":
        code_text = await fetch_github_repo(content)
        
    # Initialize client for Vertex AI using Application Default Credentials
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    
    import logging
    logger = logging.getLogger(__name__)

    # Step 1: Detect user context using the Context Engine
    context = build_code_context(code_text, intensity)
    
    logger.info(f"Roast request processed: lang={context.language.value}, "
                f"complexity={context.complexity_score}, "
                f"intensity={context.intensity.value}, "
                f"lines={context.line_count}")

    # Step 2: Build context-specific prompt
    prompt = build_analysis_prompt(context, code_text)

    # Note: text-embedding-004 logic remains here
    embedding_values = None
    try:
        embed_resp = client.models.embed_content(
            model='text-embedding-004',
            contents=code_text[:8000] # Cap size for embedding
        )
        embedding_values = embed_resp.embeddings[0].values
        logger.info(f"Generated text embeddings for input. Values count: {len(embedding_values)}")
    except Exception as e:
        logger.warning(f"Failed to generate embeddings: {e}")

    # Step 3: Call Gemini with grounding
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RoastResponse,
            tools=[{"googleSearch": {}}],
        ),
    )
    import json
    # Use exact logic to parse JSON response with potential markdown fences
    raw = response.text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)
    
    # Step 5: Save generated embedding for similarity indexing
    if embedding_values:
        result["embedding"] = embedding_values

    return result
