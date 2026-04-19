# RoastMyStack

**Challenge Vertical: Developer Tools**

> An AI-powered code reviewer that gives developers the brutal, honest feedback
> a senior engineer would — instantly, on demand, at any scale.

[![Live Demo](https://img.shields.io/badge/Live-Demo-FF4D00?style=flat)](https://roastmystack.web.app)
[![Cloud Run](https://img.shields.io/badge/Backend-Cloud%20Run-4285F4?style=flat)](https://roastmystack-api-r2itus4u2a-uc.a.run.app)

---

## Problem Statement

Developers — especially students and solo builders — lack access to fast, honest,
on-demand code review. Manual peer review is slow, socially costly, and unavailable
outside team environments. This creates a gap between code written and
production-quality code. The result: security vulnerabilities ship, bad patterns
persist, and developers don't grow as fast as they could.

## Solution

RoastMyStack uses Google Gemini 2.5 Pro to deliver instant, structured code analysis
that mirrors real senior engineer feedback. Users paste a GitHub repo URL or raw code
snippet, select a roast intensity, and receive:

1. A brutal but accurate roast identifying every significant issue
2. A severity-ranked issue list (Critical / High / Medium / Low)
3. A numbered fix plan with specific, actionable remediation steps
4. A score across 5 quality dimensions
5. A shareable unique URL for every roast session

## How It Works

```
User Input (GitHub URL or code snippet)
        ↓
FastAPI Backend (Google Cloud Run)
        ↓
GitHub API → fetch repo file contents (if URL provided)
        ↓
Gemini 2.5 Pro (Gemini API) → structured code analysis
Gemini Search Grounding → verify best practices in real-time
Gemini text-embedding-004 → generate code embedding for similarity
        ↓
Structured JSON response: { roast, issues[], fixPlan[], scores{}, embedding[] }
        ↓
Cloud Firestore → store session with unique roast ID
        ↓
Next.js Frontend → animated results page with shareable URL
```

## Google Services Used

| Service | Purpose |
|---|---|
| **Gemini 2.5 Pro** (Gemini API) | Core code analysis, roast generation, fix plan |
| **Gemini Search Grounding** | Real-time best practice verification |
| **text-embedding-004** | Code embedding for similarity matching |
| **Cloud Firestore** | Roast session storage, shareable links, user history |
| **Firebase Authentication** | GitHub OAuth login, session management |
| **Google Cloud Run** | Serverless FastAPI backend deployment |
| **Google Artifact Registry** | Docker image storage for Cloud Run |
| **Google Cloud Logging** | Structured observability and request tracking |

## Tech Stack

- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.12, deployed on Cloud Run
- **AI:** Gemini 2.5 Pro, text-embedding-004, Search Grounding
- **Database:** Cloud Firestore (Firebase)
- **Auth:** Firebase Authentication (GitHub provider)
- **Infra:** Google Cloud Run, Artifact Registry, Firebase App Hosting

## Local Setup

### Prerequisites
- Node.js 18+
- Python 3.12+
- Google Cloud project with billing enabled
- Firebase project

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Fill in your Firebase config values
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in GEMINI_API_KEY and FIREBASE_SERVICE_ACCOUNT_JSON
uvicorn main:app --reload
```

### Running Tests
```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm test
```

### Environment Variables

**frontend/.env.example:**
```
NEXT_PUBLIC_FIREBASE_API_KEY=your_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**backend/.env.example:**
```
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
FIREBASE_SERVICE_ACCOUNT_JSON={}
GITHUB_TOKEN=optional_for_higher_rate_limits
ALLOWED_ORIGINS=http://localhost:3000
```

## Assumptions

- Users provide either a valid public GitHub repository URL or raw source code
- Gemini API key has sufficient quota for the roast generation (free tier is sufficient for hackathon use)
- Firebase project has Firestore and Authentication enabled before running
- Roast sessions are public by default (shareable links); login is optional for history

## Project Structure

```
roastmystack/
├── frontend/              # Next.js 15 App Router
│   ├── src/
│   │   ├── app/           # Pages and layouts
│   │   ├── components/    # Reusable UI components
│   │   └── lib/           # Firebase client, API helpers
│   ├── __tests__/         # Frontend unit tests
│   ├── package.json
│   └── Dockerfile
├── backend/               # FastAPI on Cloud Run
│   ├── main.py            # App entry point, routes
│   ├── roast.py           # Gemini integration
│   ├── github_fetch.py    # GitHub repo content fetcher
│   ├── firebase_admin_init.py  # Firestore + Auth admin
│   ├── tests/             # Backend unit + integration tests
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```
