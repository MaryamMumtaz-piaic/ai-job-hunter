# AI Agent Architecture

## Overview

AI Job Hunter uses a **linear agent pipeline** — a series of AI-powered steps where each step's output feeds the next. Each agent is implemented as a Python function in `app/services/openai_service.py`, called from the appropriate route handler. There is no autonomous agent loop; every step is user-triggered and human-reviewable.

---

## Agent Pipeline

```
User Input (resume file + job preferences)
         │
         ▼
┌─────────────────────────────────────────┐
│         Resume Analyzer Agent           │
│  openai_service.analyze_resume()        │
│                                         │
│  Input:  raw resume text (str)          │
│  Output: structured profile (dict)      │
│  {name, email, skills[], experience[],  │
│   education[], job_titles[], summary}   │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Job Preference Processor           │
│  (UI form → preferences.json)           │
│                                         │
│  Input:  user form submission           │
│  Output: preferences record (dict)      │
│  {job_type, work_mode, titles[],        │
│   country, salary_min, salary_max,      │
│   experience_level, company_type}       │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Job Matching Agent              │
│  job_matching_service.run_matching()    │
│                                         │
│  Step 1: Local pre-filter               │
│    - Filter by work_mode, country,      │
│      experience_level, salary range     │
│    - Keyword match on titles/skills     │
│    - Reduces 150 jobs → top 50          │
│                                         │
│  Step 2: OpenAI ranking                 │
│    openai_service.match_jobs()          │
│    - Sends candidate summary + 50 jobs  │
│    - Returns scored, ranked list        │
│                                         │
│  Output per job:                        │
│    match_score (0-100)                  │
│    match_reason (str)                   │
│    matched_skills []                    │
│    missing_skills []                    │
└─────────────────────────────────────────┘
         │
         ▼
  User browses matched jobs, selects one, clicks Apply
         │
         ▼
┌─────────────────────────────────────────┐
│        Cover Letter Agent               │
│  openai_service.generate_cover_letter() │
│                                         │
│  Input:  candidate profile (dict)       │
│          job record (dict)              │
│  Output: cover letter text (str)        │
│          3-4 professional paragraphs    │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Human Approval Gate             │
│         (UI — not AI)                   │
│                                         │
│  Shows user:                            │
│    - Resume / candidate info            │
│    - Job details                        │
│    - Generated cover letter             │
│                                         │
│  User edits if needed, then clicks:     │
│    [Approve & Submit]                   │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        Application Record               │
│  application_service.create()           │
│                                         │
│  Status: Submitted                      │
│  Stored in: app/data/applications.json  │
└─────────────────────────────────────────┘
         │
         ▼
    Application Tracker (/applications)
```

---

## Agent Details

### Resume Analyzer Agent

| Property | Value |
|----------|-------|
| Function | `openai_service.analyze_resume(resume_text)` |
| Model | `gpt-4o-mini` |
| Input | Raw text extracted from uploaded file |
| Input tokens | ~2,000–4,000 (resume text) |
| Output | Structured JSON dict |
| Fallback | Mock profile data when `OPENAI_MOCK_MODE=true` |

**Output schema:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "summary": "5 years experience in...",
  "skills": ["Python", "FastAPI", "React"],
  "experience": [
    {"title": "Backend Engineer", "company": "Acme", "years": 3}
  ],
  "education": [
    {"degree": "BS Computer Science", "school": "MIT", "year": 2020}
  ],
  "years_of_experience": 5,
  "job_titles": ["Backend Engineer", "Software Engineer"],
  "industries": ["Technology", "SaaS"],
  "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"]
}
```

**Prompt strategy:** Structured JSON output with explicit field instructions. Uses `response_format={"type": "json_object"}` to guarantee parseable output.

---

### Job Matching Agent

| Property | Value |
|----------|-------|
| Function | `job_matching_service.run_matching()` then `openai_service.match_jobs()` |
| Model | `gpt-4o-mini` |
| Input | Candidate profile + preferences + up to 50 pre-filtered jobs |
| Input tokens | ~3,000–6,000 |
| Output | Ranked list of jobs with scores |
| Fallback | Score all pre-filtered jobs at 75% with generic reasons |

**Pre-filter logic (no API cost):**
```python
# 1. Work mode filter
if prefs.work_mode != "Any":
    jobs = [j for j in jobs if j["work_mode"] == prefs.work_mode]

# 2. Country filter
if prefs.country != "Any":
    jobs = [j for j in jobs if j["country"] == prefs.country]

# 3. Salary filter
if prefs.salary_min:
    jobs = [j for j in jobs if j["salary_max"] >= prefs.salary_min]

# 4. Title keyword match (scored)
# 5. Skill overlap (scored)
# → Sort by combined score, take top 50
```

**OpenAI ranking sends only:**
- job id, title, company, required skills, experience level
- NOT full description (reduces tokens by ~80%)

**Output per job:**
```json
{
  "job_id": "JOB-042",
  "match_score": 87,
  "match_reason": "Strong Python/FastAPI alignment with 3 of 5 required skills matched.",
  "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
  "missing_skills": ["Kubernetes", "Redis"]
}
```

---

### Cover Letter Agent

| Property | Value |
|----------|-------|
| Function | `openai_service.generate_cover_letter(profile, job)` |
| Model | `gpt-4o-mini` |
| Input | Candidate profile dict + job dict |
| Input tokens | ~1,200–1,800 |
| Output | Plain text cover letter (~350 words) |
| Fallback | Template cover letter with candidate and job name filled in |

**Prompt strategy:** Instructs the model to write in first person, reference specific skills from the job requirements, mention the company by name, and avoid generic filler phrases.

---

## Mock Mode

All three agents respect `OPENAI_MOCK_MODE=true`. When enabled:

- `analyze_resume()` → returns a complete realistic profile with common tech skills
- `match_jobs()` → scores the pre-filtered list with descending realistic percentages (94, 88, 82, ...)
- `generate_cover_letter()` → returns a professional 3-paragraph template letter

Mock mode is deterministic — same input produces same output. Suitable for demos and UI development.

**Enable mock mode:**
```env
OPENAI_MOCK_MODE=true
```

No API key required.

---

## Token Budget Estimates

| Operation | Est. Input Tokens | Est. Output Tokens | Est. Cost (gpt-4o-mini) |
|-----------|-------------------|-------------------|------------------------|
| Resume analysis | 2,500 | 500 | ~$0.001 |
| Job matching (50 jobs) | 4,500 | 800 | ~$0.002 |
| Cover letter | 1,500 | 400 | ~$0.001 |
| **Full flow** | **~8,500** | **~1,700** | **~$0.004** |

Total cost per complete user flow: **under $0.01** with gpt-4o-mini.

---

## Extending the Pipeline

To add a new AI agent step:

1. **Add the function** to `app/services/openai_service.py`:
```python
def my_new_agent(input_data: dict) -> dict:
    if MOCK_MODE:
        return mock_response()
    # ... OpenAI call
```

2. **Add a route** in the relevant `app/routes/*.py` file that calls your function.

3. **Add the UI** — a button in the relevant template and a JS handler in `static/js/`.

4. **Add mock data** — update the mock return to be realistic for demo use.

5. **Document it** here in `agent.md`.

---

## Error Handling

Every agent function wraps OpenAI calls in try/except:

```python
try:
    response = client.chat.completions.create(...)
    return parse_response(response)
except openai.AuthenticationError:
    raise HTTPException(403, "Invalid OpenAI API key")
except openai.RateLimitError:
    raise HTTPException(429, "OpenAI rate limit reached. Try again shortly.")
except Exception as e:
    logger.error(f"OpenAI error: {e}")
    return fallback_response()
```

Users never see raw exception traces — only friendly messages from the route layer.
