# API Reference

Base URL: `http://localhost:8000`

All API endpoints return JSON. Authentication uses session cookies set on login.

---

## Authentication

### POST /api/auth/signup

Register a new user account.

**Request body:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

**Response 201:**
```json
{
  "message": "Account created successfully",
  "user_id": "usr_abc123"
}
```

**Response 400 (email taken):**
```json
{"detail": "An account with this email already exists"}
```

**Response 422 (passwords don't match):**
```json
{"detail": "Passwords do not match"}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Smith","email":"jane@example.com","password":"pass123","confirm_password":"pass123"}'
```

---

### POST /api/auth/signin

Login and receive a session cookie.

**Request body:**
```json
{
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

**Response 200:**
```json
{
  "message": "Signed in successfully",
  "user": {
    "id": "usr_abc123",
    "full_name": "Jane Smith",
    "email": "jane@example.com"
  }
}
```
Sets cookie: `session=<signed_token>; HttpOnly; Path=/`

**Response 401:**
```json
{"detail": "Invalid email or password"}
```

**curl:**
```bash
curl -c cookies.txt -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"pass123"}'
```

---

### POST /api/auth/logout

Clear the session cookie.

**Auth:** Required

**Response 200:**
```json
{"message": "Logged out successfully"}
```

**curl:**
```bash
curl -b cookies.txt -X POST http://localhost:8000/api/auth/logout
```

---

## User & Profile

### GET /api/user

Get current authenticated user info.

**Auth:** Required

**Response 200:**
```json
{
  "id": "usr_abc123",
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "created_at": "2026-09-03T10:00:00"
}
```

---

### GET /api/profile

Get the user's full profile including resume-derived data.

**Auth:** Required

**Response 200:**
```json
{
  "user_id": "usr_abc123",
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0100",
  "location": "San Francisco, CA",
  "linkedin": "https://linkedin.com/in/janesmith",
  "github": "https://github.com/janesmith",
  "summary": "5 years of backend engineering experience...",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "experience": [
    {
      "title": "Senior Backend Engineer",
      "company": "Acme Corp",
      "start_date": "2023-01",
      "end_date": "present",
      "description": "Led API development for..."
    }
  ],
  "education": [
    {
      "degree": "BS Computer Science",
      "school": "MIT",
      "year": "2020"
    }
  ],
  "years_of_experience": 5,
  "resume_file": "/static/uploads/usr_abc123_resume.pdf",
  "portfolio_file": null
}
```

---

### PUT /api/profile

Update the user's profile.

**Auth:** Required

**Request body** (all fields optional):
```json
{
  "full_name": "Jane Smith",
  "phone": "+1-555-0100",
  "location": "Remote",
  "linkedin": "https://linkedin.com/in/janesmith",
  "github": "https://github.com/janesmith",
  "summary": "Updated summary...",
  "skills": ["Python", "FastAPI", "React", "Docker"]
}
```

**Response 200:**
```json
{"message": "Profile updated successfully"}
```

---

## Resume

### POST /api/resume/upload

Upload a resume file (PDF, DOCX, or TXT).

**Auth:** Required

**Request:** `multipart/form-data`
- `file`: The resume file (max 10MB)
- `file_type`: `"resume"` or `"portfolio"`

**Response 200:**
```json
{
  "message": "Resume uploaded successfully",
  "file_path": "/static/uploads/usr_abc123_resume.pdf",
  "file_type": "resume"
}
```

**Response 400 (invalid type):**
```json
{"detail": "Only PDF, DOCX, and TXT files are supported"}
```

**curl:**
```bash
curl -b cookies.txt -X POST http://localhost:8000/api/resume/upload \
  -F "file=@/path/to/resume.pdf" \
  -F "file_type=resume"
```

---

### POST /api/resume/analyze

Analyze the uploaded resume with OpenAI and store the structured profile.

**Auth:** Required

**Request body:**
```json
{}
```
(Uses the previously uploaded resume on file.)

**Response 200:**
```json
{
  "message": "Resume analyzed successfully",
  "profile": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "summary": "Experienced backend engineer...",
    "skills": ["Python", "FastAPI", "Docker"],
    "experience": [...],
    "education": [...],
    "years_of_experience": 5,
    "job_titles": ["Backend Engineer", "Software Engineer"],
    "industries": ["Technology"],
    "technologies": ["Python", "FastAPI", "PostgreSQL"]
  }
}
```

---

## Jobs

### GET /api/jobs

List jobs with optional filters.

**Auth:** Required

**Query parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (title, company, skills) |
| `work_mode` | string | `Remote`, `Hybrid`, `On-site` |
| `country` | string | Country filter |
| `employment_type` | string | `Full-time`, `Part-time`, `Contract` |
| `experience_level` | string | `Entry Level`, `Mid Level`, `Senior` |
| `matched` | boolean | Only return AI-matched jobs |
| `saved` | boolean | Only return saved jobs |
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20, max: 50) |

**Response 200:**
```json
{
  "jobs": [
    {
      "id": "JOB-042",
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
      "skills": ["Python", "FastAPI", "LangChain"],
      "industry": "Technology",
      "posted_date": "2026-08-20",
      "match_score": 94,
      "match_reason": "Strong alignment with AI and Python skills.",
      "is_saved": false
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

---

### GET /api/jobs/{job_id}

Get full detail for a single job.

**Auth:** Required

**Response 200:**
```json
{
  "id": "JOB-042",
  "title": "AI Engineer",
  "company": "Nova Labs",
  "company_description": "Nova Labs builds AI-powered dev tools...",
  "location": "Remote",
  "country": "United States",
  "work_mode": "Remote",
  "employment_type": "Full-time",
  "experience_level": "Mid Level",
  "salary_min": 90000,
  "salary_max": 120000,
  "currency": "USD",
  "description": "We are looking for an AI Engineer to...",
  "requirements": ["3+ years Python", "Experience with LLMs"],
  "skills": ["Python", "FastAPI", "LangChain", "OpenAI SDK"],
  "benefits": ["Remote-first", "Health insurance", "Stock options"],
  "posted_date": "2026-08-20",
  "industry": "Technology",
  "match_score": 94,
  "match_reason": "Strong alignment with AI and Python skills.",
  "matched_skills": ["Python", "FastAPI", "OpenAI SDK"],
  "missing_skills": ["LangChain"],
  "is_saved": false
}
```

---

### POST /api/jobs/analyze

Run AI job matching against user profile and preferences. This is the main analysis trigger.

**Auth:** Required

**Request body:**
```json
{
  "preferences": {
    "job_type": "Full-time",
    "work_mode": "Remote",
    "desired_titles": ["AI Engineer", "Backend Engineer"],
    "country": "United States",
    "city": "",
    "salary_min": 80000,
    "salary_max": 150000,
    "experience_level": "Mid Level",
    "company_type": "Any",
    "skills": ["Python", "FastAPI", "OpenAI"]
  }
}
```

**Response 200:**
```json
{
  "message": "Analysis complete",
  "matched_count": 23,
  "jobs": [
    {
      "id": "JOB-042",
      "title": "AI Engineer",
      "company": "Nova Labs",
      "match_score": 94,
      "match_reason": "Strong Python and AI alignment.",
      "matched_skills": ["Python", "FastAPI"],
      "missing_skills": ["Kubernetes"]
    }
  ]
}
```

---

### POST /api/jobs/{job_id}/save

Toggle save/unsave a job for the current user.

**Auth:** Required

**Response 200:**
```json
{"saved": true, "message": "Job saved"}
```
or
```json
{"saved": false, "message": "Job removed from saved"}
```

---

## Applications

### POST /api/applications

Create a new application record (starts as `Draft`).

**Auth:** Required

**Request body:**
```json
{
  "job_id": "JOB-042",
  "cover_letter": "Dear Hiring Manager, ...",
  "applicant_info": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0100",
    "location": "Remote",
    "linkedin": "https://linkedin.com/in/janesmith",
    "github": "https://github.com/janesmith"
  }
}
```

**Response 201:**
```json
{
  "id": "APP-001",
  "job_id": "JOB-042",
  "user_id": "usr_abc123",
  "status": "Draft",
  "created_at": "2026-09-03T10:30:00"
}
```

---

### GET /api/applications

List all applications for the current user.

**Auth:** Required

**Response 200:**
```json
{
  "applications": [
    {
      "id": "APP-001",
      "job_id": "JOB-042",
      "job_title": "AI Engineer",
      "company": "Nova Labs",
      "status": "Submitted",
      "applied_date": "2026-09-03T10:30:00",
      "cover_letter_preview": "Dear Hiring Manager..."
    }
  ],
  "stats": {
    "total": 1,
    "draft": 0,
    "pending": 0,
    "submitted": 1,
    "interview": 0,
    "offer": 0,
    "rejected": 0
  }
}
```

---

### GET /api/applications/{application_id}

Get full detail of a single application.

**Auth:** Required (must own the application)

**Response 200:**
```json
{
  "id": "APP-001",
  "job_id": "JOB-042",
  "user_id": "usr_abc123",
  "status": "Submitted",
  "cover_letter": "Dear Hiring Manager, I am writing to express...",
  "applicant_info": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0100"
  },
  "job": {
    "title": "AI Engineer",
    "company": "Nova Labs",
    "location": "Remote"
  },
  "created_at": "2026-09-03T10:30:00",
  "submitted_at": "2026-09-03T10:35:00"
}
```

---

### PUT /api/applications/{application_id}

Update an application (status, cover letter, etc.).

**Auth:** Required (must own the application)

**Request body** (all optional):
```json
{
  "status": "Submitted",
  "cover_letter": "Updated cover letter text...",
  "notes": "Had a great interview on Sep 10"
}
```

**Valid status transitions:**
- `Draft` → `Pending Approval`
- `Pending Approval` → `Submitted` (requires explicit approval)
- `Submitted` → `Interview`
- `Interview` → `Offer` or `Rejected`

**Response 200:**
```json
{"message": "Application updated", "status": "Submitted"}
```

---

## Cover Letter

### POST /api/cover-letter/generate

Generate a personalized cover letter using OpenAI.

**Auth:** Required

**Request body:**
```json
{
  "job_id": "JOB-042"
}
```

**Response 200:**
```json
{
  "cover_letter": "Dear Hiring Manager,\n\nI am excited to apply for the AI Engineer position at Nova Labs...\n\nSincerely,\nJane Smith",
  "generated_at": "2026-09-03T10:32:00"
}
```

**Response 503 (OpenAI unavailable):**
```json
{
  "detail": "AI service unavailable. Please try again or write your cover letter manually.",
  "fallback_available": true
}
```

---

## Error Responses

All error responses follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (validation failed, business rule violation) |
| 401 | Not authenticated (no session or session expired) |
| 403 | Forbidden (trying to access another user's data) |
| 404 | Resource not found |
| 422 | Unprocessable entity (Pydantic validation failed) |
| 429 | Rate limited (OpenAI rate limit hit) |
| 500 | Internal server error (logged server-side) |
| 503 | Service unavailable (OpenAI API down) |
