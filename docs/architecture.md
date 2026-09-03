# Architecture

## System Overview

AI Job Hunter is a monolithic web application where a single FastAPI process handles everything: HTML page serving, API endpoints, file uploads, AI calls, and local data persistence. This design keeps the MVP simple — one process to run, one port to remember, no CORS configuration, no cross-service auth.

```
┌──────────────────────────────────────────────────────┐
│                     Browser                          │
│  (HTML + Tailwind CSS + Vanilla JS)                  │
└─────────────────────┬────────────────────────────────┘
                      │ HTTP (port 8000)
┌─────────────────────▼────────────────────────────────┐
│               FastAPI + Uvicorn                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Page Routes  │  │  API Routes  │                 │
│  │ (HTML/Jinja) │  │  (JSON)      │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                          │
│  ┌──────▼─────────────────▼───────┐                 │
│  │           Services             │                 │
│  │  openai_service  resume_svc    │                 │
│  │  job_matching   application    │                 │
│  └──────────────────┬────────────┘                 │
│                     │                               │
│  ┌──────────────────▼────────────┐                  │
│  │         JSONStore             │                  │
│  │   (app/utils/json_store.py)   │                  │
│  └──────────────────┬────────────┘                  │
│                     │                               │
│  ┌──────────────────▼────────────┐                  │
│  │      app/data/*.json          │                  │
│  │  users  jobs  resumes         │                  │
│  │  applications  preferences    │                  │
│  └───────────────────────────────┘                  │
└──────────────────────────────────────────────────────┘
                      │
         (when OPENAI_MOCK_MODE=false)
                      │
┌─────────────────────▼────────────────────────────────┐
│              OpenAI API (external)                   │
│  gpt-4o-mini: resume analysis, job matching,         │
│               cover letter generation                │
└──────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### FastAPI Application (`app/main.py`)
- Creates the FastAPI app instance
- Mounts `/static` directory for CSS, JS, uploaded files
- Registers Jinja2 templates directory
- Includes all route modules
- Runs startup event that seeds `jobs.json` if empty

### Page Routes (`app/routes/pages.py`)
- `GET /` — Landing page
- `GET /signup` — Registration page
- `GET /signin` — Login page
- `GET /dashboard` — Dashboard (protected)
- `GET /analyze` — Resume + preferences page (protected)
- `GET /jobs` — Job discovery (protected)
- `GET /jobs/{id}` — Job detail (protected)
- `GET /applications` — Application tracker (protected)
- `GET /profile` — Profile editor (protected)

All page routes return `TemplateResponse`. Protected routes redirect to `/signin` if no session.

### API Routes (`app/routes/auth.py`, `jobs.py`, `profile.py`, `applications.py`)
- Accept and return JSON
- Validate input via Pydantic models
- Delegate business logic to services
- Return structured errors on failure

### Services Layer
- `openai_service.py` — All OpenAI calls, mock mode implementation
- `resume_service.py` — Coordinates file parsing + AI analysis
- `job_matching_service.py` — Local pre-filter + OpenAI ranking
- `application_service.py` — Application CRUD and status transitions

### JSONStore (`app/utils/json_store.py`)
- Single class wrapping all file I/O
- Methods: `read()`, `write()`, `find()`, `find_by_id()`, `update()`, `append()`, `delete()`
- Handles file locking to prevent corruption on concurrent writes
- Only component that directly touches `app/data/*.json` files

### Authentication (`app/utils/auth.py`)
- Session signing via `itsdangerous.URLSafeTimedSerializer`
- Password hashing via `passlib` with bcrypt
- `get_current_user()` — FastAPI dependency, reads session cookie
- `get_current_user_optional()` — For pages that work logged-in or logged-out

---

## Data Flow: Resume Analysis

```
User uploads file (POST /api/resume/upload)
        │
        ▼
file_parser.extract_text(file)
  → pdfplumber (PDF)
  → python-docx (DOCX)
  → plain read (TXT)
        │
        ▼
openai_service.analyze_resume(text)
  → if MOCK_MODE: return mock_profile
  → else: OpenAI chat completion, parse JSON response
        │
        ▼
JSONStore.update(resume_record) → resumes.json
JSONStore.update(user_profile)  → users.json
        │
        ▼
Return structured profile to client
```

---

## Data Flow: Job Matching

```
User clicks Analyze Matching Jobs (POST /api/jobs/analyze)
        │
        ▼
Load user profile from resumes.json
Load preferences from preferences.json
Load all 150 jobs from jobs.json
        │
        ▼
job_matching_service.local_prefilter(profile, prefs, jobs)
  → Apply hard filters (work_mode, country, salary)
  → Score remaining jobs by title/skill keyword overlap
  → Return top 50
        │
        ▼
openai_service.match_jobs(profile_summary, top_50_jobs)
  → if MOCK_MODE: assign descending scores 94, 88, 82...
  → else: OpenAI call with compact job summaries
        │
        ▼
Merge AI scores into job records
Store matched results in user session / resumes.json
        │
        ▼
Return ranked job list to client
```

---

## Session Management

Sessions use signed cookies (not JWTs, not server-side session store):

1. On login: create payload `{"user_id": "...", "email": "..."}`, sign with `SECRET_KEY` using itsdangerous
2. Set as `HttpOnly` cookie `session`
3. On each request: decode cookie, verify signature and expiry, load user from `users.json`
4. On logout: delete cookie

This is stateless on the server side — no session table, no Redis needed.

---

## File Upload Flow

```
POST /api/resume/upload (multipart/form-data)
        │
        ▼
Validate: extension in [.pdf, .docx, .txt]
Validate: size < 10MB
Sanitize: secure_filename(original_name)
        │
        ▼
Save to static/uploads/{user_id}_{filename}
        │
        ▼
Store file path in resumes.json for user
        │
        ▼
Return file path to client
```

Static files in `/uploads` are served by FastAPI's StaticFiles mount but the path includes the user_id prefix, making accidental cross-user access difficult (though not cryptographically enforced — MVP limitation).

---

## Design Decisions

### Why JSON files instead of SQLite?
SQLite would be a reasonable choice, but JSON files are easier to inspect, edit manually, and reset during development. The app loads each file on every request (small files, low traffic), so performance is not a concern for an MVP.

### Why itsdangerous instead of JWT?
`itsdangerous` is already a FastAPI/Starlette dependency (via Starlette's SessionMiddleware). Signed cookies work identically to JWTs for this use case — stateless, expirable, tamper-evident — with less boilerplate.

### Why Tailwind via CDN instead of build step?
The Play CDN allows full Tailwind utility usage with zero build tooling. No npm, no Node.js, no `package.json`. The constraint is that unused classes are not purged, so the CSS payload is larger (~300KB). For an MVP, this is acceptable.

### Why one server instead of frontend + backend split?
Splitting requires CORS configuration, two terminals to run, two ports to remember, and proxy setup in development. A single server with Jinja2 templates eliminates all of this. JavaScript makes async API calls to the same origin — no CORS issues.
