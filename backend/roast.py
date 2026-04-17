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

def get_system_prompt(intensity: str) -> str:
    if intensity == "junior":
        return "You are a senior software engineer acting as a mentor. Be gentle but firm in your code review. Highlight mistakes but encourage the developer. Roast them lightly."
    elif intensity == "senior":
        return "You are a busy senior engineer giving a direct, no-nonsense code review. You have no time for fluff. Point out bad patterns, security holes, and code smells clearly."
    else: # staff
        return "You are a merciless staff engineer doing a brutal code review. You have zero patience for bad code. Roast the code intensely. Use wit, sarcasm, and be brutally honest. Point out architectural sins and lazy choices."

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
    
    system_instruction = get_system_prompt(intensity)
    prompt = f"Analyze the following code and provide the output strictly adhering to the JSON schema:\n\n{code_text}"
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=RoastResponse,
        ),
    )
    
    import json
    return json.loads(response.text)
