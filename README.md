# RoastMyStack

**Challenge Vertical: Developer Tools**
**Persona: The Relentless Senior Engineer — A Smart, Dynamic Code Review Assistant**

> An AI assistant that adapts its analysis, depth, and feedback style to the
> context of your code — giving you the honest, senior-level review that most
> developers never get.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-FF4D00?style=for-the-badge)](https://roastmystack-main-u6tztid3wa-uc.a.run.app/)
[![Vertical](https://img.shields.io/badge/Vertical-Developer%20Tools-4285F4?style=for-the-badge)]()
[![Google Services](https://img.shields.io/badge/Google%20Services-7%20Integrated-34A853?style=for-the-badge)]()

---

## Challenge Vertical: Developer Tools

### The Problem

Junior and mid-level developers lack consistent access to honest, senior-level
code review. Manual peer review is slow, socially costly, and inaccessible to
solo builders and students. This gap between written code and production-quality
code creates real-world consequences: security vulnerabilities ship, bad
architectural patterns calcify, and developers stagnate.

### The Solution: A Smart, Dynamic Assistant

RoastMyStack is not a static analysis tool. It is a **smart assistant that makes
logical decisions based on user context** at every stage of the review process.

The assistant:
1. **Detects input context** — GitHub URL vs raw code, language, file size,
   repository structure
2. **Adapts analysis depth** — based on detected code complexity and selected
   experience level
3. **Applies language-specific logic** — different heuristics for Python,
   JavaScript, TypeScript, and more
4. **Prioritizes issues by real-world severity** — not style preferences
5. **Generates a contextual fix plan** — specific to the exact issues found,
   with before/after code examples

See [VERTICAL.md](./VERTICAL.md) for the full decision-making logic breakdown.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  User Input: GitHub URL or Code Snippet + Intensity     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Context Detection Layer (FastAPI — Cloud Run)           │
│  • Input type: URL vs snippet                            │
│  • Language auto-detection                               │
│  • Code complexity scoring                               │
│  • Repository structure analysis (if URL)               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Adaptive Prompt Construction                            │
│  • Selects analysis depth based on complexity + level    │
│  • Applies language-specific rule sets                   │
│  • Sets severity weighting based on code patterns found  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Gemini 2.5 Pro — Structured Code Analysis               │
│  + Search Grounding (real-time best practice lookup)     │
│  + text-embedding-004 (similarity indexing)              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Structured Output:                                      │
│  roast | issues[] | fixPlan[] | scores{} | context{}     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Firestore — Session storage, shareable URL generation   │
│  Cloud Logging — Observability, request tracking         │
└─────────────────────────────────────────────────────────┘
```

## Contextual Decision Making — Core Logic

The assistant's behavior changes based on user context. This is the smart
assistant layer, not just a prompt wrapper.

### Language-Specific Analysis

```python
# backend/context_engine.py

LANGUAGE_RULES = {
    "python": [
        "Check for missing type hints on public functions",
        "Verify context managers used for file/resource handling",
        "Check for bare except clauses",
        "Verify f-strings over .format() for modern Python",
        "Check for mutable default arguments",
    ],
    "javascript": [
        "Check for == vs === comparisons",
        "Verify async/await error handling with try/catch",
        "Check for var usage (should be const/let)",
        "Identify potential null/undefined access patterns",
        "Check for console.log statements left in production code",
    ],
    "typescript": [
        "Check for 'any' type usage",
        "Verify strict null checks are respected",
        "Check for proper interface vs type usage",
        "Identify missing return type annotations",
    ],
    "general": [
        "Security: injection risks, exposed secrets, auth issues",
        "Naming: variables, functions, classes must be descriptive",
        "Structure: single responsibility, appropriate abstractions",
        "Error handling: all failure paths must be handled",
    ]
}

def get_analysis_rules(language: str, complexity_score: int) -> list[str]:
    """
    Logical decision: selects which rules to apply based on
    detected language and code complexity score.
    High complexity code gets all rules.
    Low complexity code focuses on critical issues only.
    """
    base_rules = LANGUAGE_RULES.get("general", [])
    lang_rules = LANGUAGE_RULES.get(language.lower(), [])

    if complexity_score > 70:
        return base_rules + lang_rules
    elif complexity_score > 40:
        return base_rules + lang_rules[:3]
    else:
        return base_rules
```

### Intensity-Based Persona Adaptation

```python
INTENSITY_PERSONAS = {
    "junior": {
        "tone": "educational but direct",
        "focus": "explain why each issue matters, use analogies",
        "depth": "surface-level patterns and common beginner mistakes",
        "output_style": "constructive with clear before/after examples"
    },
    "senior": {
        "tone": "blunt and professional",
        "focus": "architectural issues, maintainability, production risks",
        "depth": "systemic patterns, not just individual lines",
        "output_style": "honest assessment with prioritized fix plan"
    },
    "staff": {
        "tone": "merciless and precise",
        "focus": "scalability, security posture, team impact, tech debt",
        "depth": "full architectural review, long-term consequences",
        "output_style": "executive-level assessment with immediate action items"
    }
}
```

## Google Services Integration

| Service | Role in Assistant Logic |
|---|---|
| **Gemini 2.5 Pro** | Core analysis engine — contextual code review |
| **Gemini Search Grounding** | Real-time best practice lookup during analysis |
| **text-embedding-004** | Code vector embedding for session similarity |
| **Cloud Firestore** | Session persistence, shareable roast URLs |
| **Firebase Authentication** | GitHub OAuth, user history tracking |
| **Google Cloud Run** | Serverless backend — scales to zero |
| **Google Cloud Logging** | Structured request observability |

## Tech Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.12, Google Cloud Run
- **AI:** Gemini 2.5 Pro, text-embedding-004, Search Grounding
- **Database:** Cloud Firestore
- **Auth:** Firebase Auth (GitHub provider)
- **Observability:** Google Cloud Logging

## Local Setup

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Tests
```bash
cd backend && pytest tests/ -v
cd frontend && npm test
```

## Assumptions

- Users submit either a valid public GitHub repo URL or raw source code
- Language is auto-detected; users do not need to specify it manually
- The assistant adapts its review depth to detected code complexity
- Roast sessions are publicly accessible via shareable URL by default
- Firebase Auth login is optional — required only for history persistence
