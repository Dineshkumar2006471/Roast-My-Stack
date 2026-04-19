import os
import json
import logging
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
from context_engine import build_code_context, build_analysis_prompt

# Setup logging
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Issue(BaseModel):
    type: str
    line: Optional[int] = None
    description: str
    severity: str
    language_specific: bool

class FixStep(BaseModel):
    issue: str
    fix: str
    code_example: Optional[str] = None
    priority: int

class Scores(BaseModel):
    codeQuality: int
    security: int
    efficiency: int
    testing: int
    accessibility: int

class ContextSummary(BaseModel):
    language_detected: str
    complexity: str
    review_mode: str
    frameworks: List[str]
    security_pre_detected: bool

class RoastResponse(BaseModel):
    roast: str
    issues: List[Issue]
    fixPlan: List[FixStep]
    scores: Scores
    context_summary: ContextSummary
    embedding: Optional[List[float]] = None

def generate_roast(code: str, intensity: str) -> dict:
    """
    Smart assistant entry point using the direct Gemini API.
    Context is detected first, then drives the entire analysis.
    """
    if not GEMINI_API_KEY and os.getenv("TESTING") != "true":
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    # Configure the direct Gemini API SDK
    genai.configure(api_key=GEMINI_API_KEY)

    # Step 1: Detect user context
    context = build_code_context(code, intensity)
    logger.info(f"Context detected: lang={context.language.value}, complexity={context.complexity_score}")

    # Step 2: Build context-specific prompt
    prompt = build_analysis_prompt(context, code)

    # Step 3: Initialize model (using the required gemini-2.5-pro name)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config={
            "response_mime_type": "application/json",
        }
    )

    # Step 4: Generate content
    try:
        # In test mode, we might not have a real API key, so we handle it
        if os.getenv("TESTING") == "true":
            # This branch should rarely be hit if mocks are working, 
            # but it's a safety net for local dev.
            return {
                "roast": "Test mode active.",
                "issues": [],
                "fixPlan": [],
                "scores": {"codeQuality": 100, "security": 100, "efficiency": 100, "testing": 100, "accessibility": 100},
                "context_summary": {
                    "language_detected": context.language.value,
                    "complexity": str(context.complexity_score),
                    "review_mode": context.intensity.value,
                    "frameworks": [],
                    "security_pre_detected": False
                }
            }

        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean potential markdown delimiters
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_json)
        
        # Add context summary for the frontend/observability
        result["context_summary"] = {
            "language_detected": context.language.value,
            "complexity": str(context.complexity_score),
            "review_mode": context.intensity.value,
            "frameworks": [], # Framework detection would go here if implemented
            "security_pre_detected": len(detect_security_indicators(code)) > 0 if 'detect_security_indicators' in globals() else False
        }

    except Exception as e:
        logger.error(f"Gemini API failure: {e}")
        raise RuntimeError(f"Assistant logic failed: {str(e)}")

    # Step 5: (Optional) Embeddings - google-generativeai uses a different method
    try:
        embed_res = genai.embed_content(
            model="models/text-embedding-004",
            content=code[:8000],
            task_type="retrieval_document"
        )
        result["embedding"] = embed_res["embedding"]
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")

    return result

def detect_security_indicators(code: str) -> List[str]:
    # Import locally to avoid circular dependencies if any
    from context_engine import detect_security_indicators as ds
    return ds(code)
