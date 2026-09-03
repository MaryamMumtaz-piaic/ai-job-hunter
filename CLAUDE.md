# AI Job Hunter — Claude Code Instructions

## Project Overview

This is a **single-server FastAPI MVP** — FastAPI serves HTML via Jinja2 templates AND exposes JSON API endpoints. Everything runs at `http://localhost:8000`. There is no separate frontend server, no Node.js, no npm.

---

## Development Commands

```bash
# Run the application
uvicorn app.main:app --reload --port 8000

# Install dependencies
pip install -r requirements.txt

# Regenerate job dataset (if needed)
python seed/generate_jobs.py
```

---

## Architecture Decisions

| Decision | Reason |
|----------|--------|
| JSON files as database | MVP simplicity — no DB setup required |
| Sessions via itsdangerous | No JWT complexity; cookie-based sessions |
| Tailwind CSS via CDN | No build step; no npm required |
| Single FastAPI server | Serves templates + API; no CORS issues |
| passlib/bcrypt | Secure password hashing; no plaintext passwords |
| pdfplumber + python-docx | Reliable local file parsing; no external APIs |

---

## Important Patterns

### Data Access
All data goes through `app/utils/json_store.py` — never read/write JSON files directly in routes or services.

```python
from app.utils.json_store import JSONStore

store = JSONStore("app/data/users.json")
user = store.find_by_id(user_id)
store.update(user_id, {"name": "New Name"})
```

### Authentication
Sessions managed in `app/utils/auth.py`. Use `get_current_user()` dependency in protected routes.

```python
from app.utils.auth import get_current_user
from fastapi import Depends

@router.get("/api/profile")
async def get_profile(user=Depends(get_current_user)):
    ...
```

### Template Rendering
All templates inherit from `templates/base.html`. Pass `request` and `user` to every template context.

```python
return templates.TemplateResponse("dashboard.html", {
    "request": request,
    "user": user,
})
```

### API vs Page Routes
- `app/routes/pages.py` — GET routes returning HTML templates
- `app/routes/auth.py`, `jobs.py`, `profile.py`, `applications.py` — POST/GET/PUT returning JSON

---

## File Ownership Map

| Path | Purpose |
|------|---------|
| `app/main.py` | App factory, mounts, startup events |
| `app/routes/` | HTTP handlers — thin, delegate to services |
| `app/services/` | Business logic, OpenAI calls |
| `app/models/` | Pydantic request/response models |
| `app/utils/json_store.py` | All file I/O |
| `app/utils/auth.py` | Session + password utilities |
| `app/utils/file_parser.py` | PDF/DOCX/TXT text extraction |
| `app/data/*.json` | Persistent data (git-ignored except jobs.json) |
| `templates/` | Jinja2 HTML templates |
| `static/js/` | Page-specific vanilla JS modules |
| `static/css/styles.css` | Custom styles beyond Tailwind |
| `static/uploads/` | Uploaded resume files (git-ignored) |

---

## OpenAI Integration

All OpenAI calls live in `app/services/openai_service.py`. Three functions:

```python
analyze_resume(resume_text: str) -> dict
match_jobs(candidate_profile: dict, preferences: dict, jobs: list) -> list
generate_cover_letter(profile: dict, job: dict) -> str
```

When `OPENAI_MOCK_MODE=true`, these functions return deterministic mock data. Never call OpenAI directly from routes.

---

## Testing

```bash
# Test with mock mode (no API key needed)
OPENAI_MOCK_MODE=true uvicorn app.main:app --reload --port 8000

# Manual flow test
# 1. Sign up at /signup
# 2. Sign in at /signin
# 3. Go to dashboard, click Analyze My Resume
# 4. Upload a PDF resume
# 5. Set preferences, click Analyze Matching Jobs
# 6. Browse results, click Apply on a job
# 7. Generate cover letter, approve application
# 8. Check /applications tracker

# API test with curl
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `jobs.json` is empty after startup | Server auto-seeds on startup; check console for errors |
| Session not persisting | Ensure `SECRET_KEY` is set in `.env` |
| File upload fails | Check `static/uploads/` directory exists and is writable |
| OpenAI 401 error | Set valid `OPENAI_API_KEY` or use `OPENAI_MOCK_MODE=true` |
| Template not found | Check `templates/` directory and Jinja2 mount path in `main.py` |
| Import errors | Ensure all `__init__.py` files exist in `app/`, `app/routes/`, etc. |

---

## Do Not

- Add React, Vue, Next.js, Angular, or any JS framework
- Add PostgreSQL, Redis, MongoDB, or any external database
- Add Celery, RQ, or any task queue
- Add Docker unless explicitly requested
- Add a separate frontend dev server (Vite, Webpack, etc.)
- Call OpenAI directly from routes — always go through `openai_service.py`
- Read/write JSON data files directly — always use `JSONStore`
- Store plaintext passwords
- Expose `app/data/` directory via static file serving
- Hardcode API keys anywhere in source files

---

## Style Guide

- Python: follow PEP 8, use type hints on function signatures
- Jinja2: keep logic minimal; push computation to routes/services
- JavaScript: ES6+, `async/await`, no frameworks
- Tailwind: utility-first; add custom CSS in `styles.css` only when Tailwind can't do it
- Comments: only for non-obvious business rules or workarounds
