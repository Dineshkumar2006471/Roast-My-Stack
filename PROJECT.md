# RoastMyStack — Project Specification

> AI Code Roaster with Brutal Honest Feedback
> Built for PromptWars Virtual | Google Antigravity + Google AI Services

---

## What Are We Building?

**RoastMyStack** is a web application where developers paste a GitHub repo URL or raw code snippet and receive two things:

1. A **brutal, honest roast** of their code — written in the voice of a senior engineer with zero patience — identifying bad patterns, lazy naming, security holes, architectural sins, and code smells.
2. A **structured fix plan** — precise, actionable steps to actually fix every issue raised in the roast, ranked by severity.

The roast is shareable via a unique URL. Users can log in with GitHub to save roast history and track improvement over time. Every roast is scored across 6 evaluation axes that mirror the PromptWars AI scoring criteria.

**Primary users:** developers (students, freelancers, professionals) who want honest feedback without the social cost of asking a colleague.

---

## How It Works — User Flow

```
User lands on homepage
        ↓
Pastes GitHub repo URL OR raw code snippet
        ↓
Selects roast intensity: "Junior Review" / "Senior Review" / "Staff Engineer Wrath"
        ↓
Optionally: logs in with GitHub (Firebase Auth) to save session
        ↓
Hits "Roast My Code"
        ↓
Backend (Cloud Run) fetches repo content via GitHub API (if URL) 
or accepts raw code directly
        ↓
Code is passed to Gemini 2.5 Pro via Gemini API with structured prompt
        ↓
Gemini returns:
  - Roast text (brutal, witty, precise)
  - Structured JSON: { issues[], severity[], fixPlan[], scores{} }
        ↓
Frontend renders animated roast reveal + fix plan card
        ↓
Unique shareable URL generated, session saved to Firestore
        ↓
User can share on LinkedIn/Twitter (pre-filled post template)
```

---

## Architecture

### High-Level

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                     │
│         Next.js 15 App Router — Static Export           │
│    Firebase Auth SDK | Firebase JS SDK (Firestore)      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────┐
│               API LAYER (Cloud Run)                      │
│               FastAPI — Python 3.12                      │
│  /api/roast   /api/fetch-repo   /api/session             │
└──────┬────────────────┬─────────────────────────────────┘
       │                │
┌──────▼──────┐  ┌──────▼──────────────────────────────────┐
│ Gemini API  │  │  Firebase Admin SDK                      │
│ (via Vertex │  │  Firestore (roast sessions, history)     │
│  AI or      │  │  Firebase Auth (GitHub OAuth)            │
│  AI Studio) │  └──────────────────────────────────────────┘
└─────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│  Gemini's Grounding Tool (Google Search)                 │
│  Used to verify best practices in real-time              │
└─────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 15 (App Router, static export) | UI, auth state, Firestore reads |
| Styling | Tailwind CSS | Utility-first styling |
| Backend API | FastAPI on Cloud Run | Orchestrates Gemini calls, GitHub fetch |
| AI Model | Gemini 2.5 Pro (via Gemini API) | Code analysis, roast generation, fix plan |
| Grounding | Gemini Search Grounding | Real-time best practice verification |
| Database | Cloud Firestore | Roast sessions, shareable links, user history |
| Auth | Firebase Auth (GitHub provider) | Optional login, session persistence |
| Hosting (Frontend) | Firebase App Hosting OR Vercel | Static Next.js deployment |
| Hosting (Backend) | Cloud Run (serverless) | FastAPI container |
| Container Registry | Google Artifact Registry | Store Docker image for Cloud Run |

---

## Google AI Services — Complete Integration List

### 1. Gemini 2.5 Pro (Core AI Engine)
- **Used for:** Code analysis, roast generation, fix plan creation, severity scoring
- **How:** Called from FastAPI backend via `google-generativeai` Python SDK
- **Key features used:**
  - System instruction: persona of a brutal senior engineer
  - JSON mode / structured output: returns `{ roast, issues[], fixPlan[], scores{} }`
  - Long context window: handles full repo files
  - Code understanding: natively understands syntax across languages

**Model string:** `gemini-2.5-pro` (via AI Studio key) or `gemini-2.5-pro-preview-0506` (via Vertex AI)

**Prompt strategy:**
```
System: You are a brutally honest senior software engineer with 15 years of experience 
and zero patience for bad code. You roast code like you're reviewing a PR from an intern 
who should have known better. Be specific, be funny, be merciless — but always accurate.

User: [code content]
Roast intensity: [junior/senior/staff]

Respond ONLY in this JSON structure:
{
  "roast": "string (the brutal roast, 150-300 words)",
  "issues": [{ "type": string, "line": number|null, "description": string, "severity": "critical|high|medium|low" }],
  "fixPlan": [{ "issue": string, "fix": string, "priority": number }],
  "scores": { "codeQuality": 0-100, "security": 0-100, "efficiency": 0-100, "testing": 0-100, "accessibility": 0-100 }
}
```

### 2. Gemini Search Grounding
- **Used for:** When Gemini identifies an issue, it can ground its fix suggestions against real-time Google Search results for current best practices
- **How:** Enable `tools=[Tool(google_search_retrieval=GoogleSearchRetrieval())]` in the API call
- **Example:** "Use parameterized queries instead of string interpolation" — grounded against current OWASP guidelines

### 3. Cloud Firestore
- **Used for:** Storing roast sessions with unique IDs, user roast history, leaderboard data (most-roasted repos)
- **Collection structure:**
  ```
  roasts/
    {roastId}/
      userId: string | null
      codeHash: string
      roastText: string
      issues: array
      fixPlan: array
      scores: map
      createdAt: timestamp
      shareUrl: string
      language: string
      intensity: string
  
  users/
    {userId}/
      email: string
      githubUsername: string
      roastCount: number
      lastRoastAt: timestamp
  ```

### 4. Firebase Authentication (GitHub Provider)
- **Used for:** Optional GitHub OAuth login
- **Why optional:** Lowers friction. Anonymous users can still get roasts but can't save history.
- **Implementation:** Firebase Auth JS SDK on the frontend, Firebase Admin SDK on the backend for token verification

### 5. Cloud Run
- **Used for:** Hosting the FastAPI backend
- **Why Cloud Run:** Serverless, scales to zero (no cost when idle), perfect for a hackathon project
- **Container:** Dockerfile with Python 3.12 + FastAPI + uvicorn
- **Memory:** 512 MB (sufficient for Gemini API calls)
- **Region:** `asia-south1` (Mumbai — low latency for India)

### 6. Google Artifact Registry
- **Used for:** Storing the Docker image before deploying to Cloud Run
- **Command flow:**
  ```bash
  docker build -t roast-api .
  docker tag roast-api asia-south1-docker.pkg.dev/[PROJECT_ID]/roastmystack/api:latest
  docker push asia-south1-docker.pkg.dev/[PROJECT_ID]/roastmystack/api:latest
  gcloud run deploy roast-api --image [IMAGE_URL] --region asia-south1
  ```

### 7. Firebase App Hosting (Frontend)
- **Used for:** Deploying the Next.js frontend
- **Alternative:** Vercel (faster CI/CD for Next.js)
- **Recommendation:** Use Firebase App Hosting to maximize Google Services score

---

## API Keys & Environment Variables

### What You Need to Set Up

#### Google AI Studio (Gemini API Key)
1. Go to: https://aistudio.google.com/apikey
2. Create a new API key
3. Use model: `gemini-2.5-pro`
4. **Cost:** Free tier is generous for a hackathon

#### Firebase Project
1. Go to: https://console.firebase.google.com
2. Create project: `roastmystack`
3. Enable:
   - Firestore Database (production mode, then set rules)
   - Authentication → GitHub provider
     - Requires GitHub OAuth App (Settings → Developer Settings → OAuth Apps)
     - Callback URL: `https://[your-project].firebaseapp.com/__/auth/handler`
4. Download `serviceAccountKey.json` for backend (Cloud Run secret)

#### GitHub OAuth App (for Firebase GitHub Auth)
1. Go to: https://github.com/settings/developers
2. New OAuth App
3. Callback URL: Firebase gives you this when you enable GitHub provider
4. Copy Client ID and Client Secret into Firebase Console

### Environment Variables

**Frontend (.env.local)**
```env
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_API_BASE_URL=https://[your-cloud-run-url]
```

**Backend (Cloud Run Secret Manager)**
```env
GEMINI_API_KEY=                    # From AI Studio
FIREBASE_SERVICE_ACCOUNT_JSON=     # Full JSON content of serviceAccountKey.json
GITHUB_TOKEN=                      # Optional: GitHub PAT for higher rate limits on repo fetch
ALLOWED_ORIGINS=https://[frontend-domain]
```

---

## MCP Servers to Connect in Google Antigravity

Open Antigravity → Settings → MCP Servers → Add the following:

### 1. Firebase MCP (Official)
```json
{
  "name": "firebase",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "firebase-tools@latest", "experimental:mcp"],
  "env": {
    "FIREBASE_TOKEN": "[your-firebase-cli-token]"
  }
}
```
**What it gives you:** Antigravity agents can read/write Firestore, manage Auth, deploy to Firebase App Hosting, view rules — all from within the IDE.

### 2. Google Cloud Run MCP (via gcloud CLI)
```json
{
  "name": "gcloud",
  "type": "stdio", 
  "command": "npx",
  "args": ["-y", "@google-cloud/mcp-server"],
  "env": {
    "GOOGLE_CLOUD_PROJECT": "[your-project-id]"
  }
}
```
**What it gives you:** Agents can deploy to Cloud Run, check service logs, manage container images — without leaving Antigravity.

### 3. GitHub MCP (Official)
```json
{
  "name": "github",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "[your-github-pat]"
  }
}
```
**What it gives you:** Agents can fetch repo contents, read files, check commit history — critical for the core feature of fetching a GitHub repo to roast.

### 4. Context7 MCP (for up-to-date library docs)
```json
{
  "name": "context7",
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"]
}
```
**What it gives you:** When Antigravity agents write code using Next.js 15, FastAPI, Firebase SDK, Gemini SDK — they pull current, version-accurate documentation. Prevents outdated API usage.

---

## Repository Structure (Under 10 MB)

```
roastmystack/
├── frontend/                    # Next.js 15 App
│   ├── app/
│   │   ├── page.tsx             # Landing + input form
│   │   ├── roast/[id]/page.tsx  # Roast results + shareable
│   │   ├── history/page.tsx     # User's roast history (authenticated)
│   │   └── layout.tsx
│   ├── components/
│   │   ├── RoastInput.tsx
│   │   ├── RoastCard.tsx
│   │   ├── ScoreBoard.tsx
│   │   ├── FixPlan.tsx
│   │   └── ShareButton.tsx
│   ├── lib/
│   │   ├── firebase.ts          # Firebase client init
│   │   └── api.ts               # API client calls
│   └── package.json
│
├── backend/                     # FastAPI on Cloud Run
│   ├── main.py                  # FastAPI app entry
│   ├── roast.py                 # Gemini integration logic
│   ├── github_fetch.py          # GitHub repo content fetcher
│   ├── firebase_admin.py        # Firestore + Auth admin
│   ├── requirements.txt
│   └── Dockerfile
│
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD: Cloud Run + Firebase deploy
│
├── PROJECT.md                   # This file
├── DESIGN.md                    # Frontend design specification
└── README.md                    # For judges: setup, demo, architecture
```

**Size control:**
- No `node_modules` (gitignored)
- No Python `venv` (gitignored)
- No build artifacts (`/.next`, `/dist` gitignored)
- No large assets — all icons from Lucide React (zero weight)
- Estimated repo size: **~2–3 MB** (mostly TypeScript and Python source)

---

## Evaluation Criteria Coverage

| Criterion | How RoastMyStack Covers It |
|---|---|
| **Code Quality** | Gemini explicitly scores this and calls out issues — the app's core output |
| **Security** | Gemini identifies SQL injection, exposed secrets, auth flaws — dedicated severity level |
| **Efficiency** | Performance issues (N+1 queries, unnecessary loops) are a roast category |
| **Testing** | Missing tests are flagged; fix plan includes test recommendations |
| **Accessibility** | Frontend built with semantic HTML, ARIA labels, keyboard navigation |
| **Google Services** | Gemini API, Firebase Auth, Firestore, Cloud Run, Artifact Registry, Search Grounding |

---

## What Makes This Top-100 Quality

1. **Core feature is genuinely useful** — not a demo, an actual tool developers will bookmark
2. **Six Google services deeply integrated** — not superficially bolted on
3. **Shareable output** — every roast has a public URL, which drives organic visibility
4. **Blog narrative writes itself** — "I built an AI that roasts code and it roasted mine first"
5. **Under 10 MB with room to spare** — clean, focused codebase
6. **Built entirely in Antigravity** — judges can see agent logs and plan artifacts in your blog screenshots
7. **Mirrors the evaluation criteria** — the app scores code on the exact same axes the judges use
