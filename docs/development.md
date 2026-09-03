# Development Guide

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/MaryamMumtaz-piaic/ai-job-hunter.git
cd ai-job-hunter

python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- Set `SECRET_KEY` to any long random string
- Leave `OPENAI_MOCK_MODE=true` for development (no API key needed)
- Add `OPENAI_API_KEY` only when testing real AI features

### 3. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000 — jobs are auto-seeded on first start.

---

## Running in Mock Mode

Mock mode simulates all OpenAI responses locally — no API key, no cost, instant responses.

```env
OPENAI_MOCK_MODE=true
```

What mock mode returns:
- **Resume analysis**: A realistic profile with common tech skills (Python, FastAPI, React, etc.)
- **Job matching**: Scores pre-filtered jobs with descending realistic percentages (94%, 88%, 82%...)
- **Cover letter**: A professional 3-paragraph letter with the candidate name and job title filled in

Mock mode is deterministic — the same input always produces the same output. Good for automated testing and demos.

---

## Adding New Jobs to the Dataset

### Option A: Edit `app/data/jobs.json` directly

Each job follows this schema:
```json
{
  "id": "JOB-201",
  "title": "AI Engineer",
  "company": "Nova Labs",
  "location": "Remote",
  "country": "United States",
  "work_mode": "Remote",
  "employment_type": "Full-time",
  "experience_level": "Mid Level",
  "salary_min": 90000,
  "salary_max": 120000,
  "currency": "USD",
  "description": "We are building the next generation of...",
  "requirements": ["3+ years Python", "Experience with LLMs"],
  "skills": ["Python", "FastAPI", "LangChain"],
  "benefits": ["Remote-first", "Health insurance"],
  "posted_date": "2026-09-01",
  "company_description": "Nova Labs is a seed-stage AI startup...",
  "industry": "Technology"
}
```

Make sure `id` values are unique.

### Option B: Regenerate the full dataset

```bash
python seed/generate_jobs.py
```

This overwrites `app/data/jobs.json` with a fresh set of 150 dummy jobs.

---

## Extending the OpenAI Agents

### Adding a new AI function

1. Open `app/services/openai_service.py`

2. Add your function following the existing pattern:

```python
def my_new_agent(input_data: dict) -> dict:
    """Brief description of what this agent does."""
    if MOCK_MODE:
        return _mock_my_new_agent(input_data)
    
    prompt = f"""
    Your prompt here.
    Input: {json.dumps(input_data, indent=2)}
    Return JSON with fields: ...
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"my_new_agent error: {e}")
        return _mock_my_new_agent(input_data)

def _mock_my_new_agent(input_data: dict) -> dict:
    return {"result": "mock result", "field": "value"}
```

3. Add a route in the relevant `app/routes/*.py` file that calls your function.

4. Add the UI trigger in the template and JS handler.

5. Document the new agent in `agent.md`.

---

## Debugging Tips

### Server won't start

```bash
# Check for import errors
python -c "from app.main import app"

# Check requirements installed
pip install -r requirements.txt

# Check Python version (need 3.11+)
python --version
```

### Jobs not showing after analysis

1. Check `app/data/jobs.json` is not empty (should have 150 jobs)
2. Check `app/data/resumes.json` has an entry for your user
3. Check browser console for API errors (F12 → Network tab)
4. Check server console for Python tracebacks

### Session not persisting between pages

- Ensure `SECRET_KEY` is set in `.env` (not empty)
- Check that cookies are enabled in your browser
- The session cookie is `HttpOnly` — you won't see it in JS `document.cookie`, but it appears in DevTools → Application → Cookies

### OpenAI errors

| Error message | Cause | Fix |
|--------------|-------|-----|
| `AuthenticationError` | Wrong API key | Check `OPENAI_API_KEY` in `.env` |
| `RateLimitError` | Too many requests | Wait 60 seconds or enable mock mode |
| `APIConnectionError` | No internet / OpenAI down | Check connectivity or enable mock mode |
| `JSONDecodeError` | Model returned non-JSON | Retry; or check prompt in `openai_service.py` |

### File upload fails

```bash
# Ensure uploads directory exists and is writable
ls static/uploads/

# On Windows, check no antivirus is blocking the directory
```

---

## Common Development Patterns

### Reading data in a route

```python
from app.utils.json_store import JSONStore

store = JSONStore("app/data/applications.json")
applications = store.find({"user_id": current_user["id"]})
```

### Protected route

```python
from app.utils.auth import get_current_user
from fastapi import Depends

@router.get("/api/my-data")
async def my_route(user = Depends(get_current_user)):
    # user is a dict with id, email, full_name
    return {"user_id": user["id"]}
```

### Returning a template with user context

```python
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@router.get("/my-page")
async def my_page(request: Request, user = Depends(get_current_user)):
    return templates.TemplateResponse("my_page.html", {
        "request": request,
        "user": user,
        "page_title": "My Page",
    })
```

### Adding a toast notification from JS

```javascript
// main.js exports showToast globally
showToast("Operation successful", "success");
showToast("Something went wrong", "error");
showToast("Please wait...", "info");
```

### Making an authenticated API call from JS

```javascript
const response = await fetch("/api/my-endpoint", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({key: "value"}),
    credentials: "include",  // sends session cookie
});

if (!response.ok) {
    const err = await response.json();
    showToast(err.detail || "Something went wrong", "error");
    return;
}

const data = await response.json();
```

---

## Data Files Reference

| File | Description | Cleared on... |
|------|-------------|---------------|
| `app/data/users.json` | User accounts (id, email, hashed_password) | Never (manual) |
| `app/data/jobs.json` | 150 dummy job listings | `python seed/generate_jobs.py` |
| `app/data/resumes.json` | Parsed resume profiles per user | Never (manual) |
| `app/data/applications.json` | Application records | Never (manual) |
| `app/data/preferences.json` | Job preferences per user | Never (manual) |

To reset to a clean state for testing:
```bash
echo "[]" > app/data/users.json
echo "[]" > app/data/resumes.json
echo "[]" > app/data/applications.json
echo "[]" > app/data/preferences.json
# jobs.json auto-reseeds on next server start if empty
```

---

## Project Conventions

- **No comments** unless the WHY is non-obvious
- **Type hints** on all function signatures
- **Services, not routes** — keep routes thin; business logic goes in `app/services/`
- **JSONStore always** — never `open("app/data/foo.json")` directly in a route
- **Pydantic models** for all request bodies (not raw dicts from `await request.json()`)
- **Graceful fallback** — every OpenAI call must have a working fallback
- **User ownership** — always verify `application["user_id"] == current_user["id"]` before returning sensitive data
