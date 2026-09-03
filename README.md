# AI Job Hunter

> AI-powered job discovery and application assistant

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## Overview

AI Job Hunter is a local MVP web application that uses OpenAI to help you discover, analyze, and apply for jobs intelligently. Upload your resume, set your job preferences, and let the AI match you with opportunities from a curated job dataset — complete with match scores, skill gap analysis, personalized cover letters, and a human-in-the-loop approval workflow before any application is recorded.

Everything runs from a single FastAPI server. No external job boards are scraped or submitted to. All data is stored locally in JSON files.

---

## Features

- **AI Resume Analysis** — Upload PDF, DOCX, or TXT; OpenAI extracts structured profile data (skills, experience, education, job titles)
- **Intelligent Job Matching** — Local pre-filter + OpenAI ranking produces match scores (e.g. 94%) with explained reasoning
- **Skill Gap Analysis** — See matched skills, missing skills, and why each job fits your profile
- **Personalized Cover Letter Generation** — One-click AI cover letters tuned to the specific job and your background
- **Human Approval Workflow** — Review every detail before an application is recorded; nothing submits without your explicit approval
- **Application Tracking** — Full lifecycle: Draft → Pending Approval → Submitted → Interview → Offer/Rejected
- **Job Preference Management** — Job type, work mode, location, salary range, experience level, company type
- **Profile Management** — Edit resume-derived information, skills, experience, and preferences
- **Mock Mode** — Full functionality without an OpenAI API key for development and demo use
- **Local JSON Persistence** — No database setup required; all data lives in readable JSON files

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Templates | Jinja2 |
| Frontend | Tailwind CSS (CDN), Vanilla JavaScript |
| AI | OpenAI GPT-4o-mini |
| Storage | Local JSON files |
| Auth | Session-based (itsdangerous) |
| Password Hashing | passlib + bcrypt |
| File Parsing | pdfplumber, python-docx |
| Environment | python-dotenv |

---

## Architecture

The application follows a clean service-oriented architecture where FastAPI serves both the HTML frontend (via Jinja2 templates) and the JSON API. A single server handles everything — no separate frontend build step, no Node.js, no separate dev server.

```
Browser ──HTTP──▶ FastAPI (Uvicorn)
                      │
              ┌───────┼───────────┐
              │       │           │
          Routes   Services    Templates
              │       │           │
          auth.py  openai_     base.html
          jobs.py  service.py  dashboard.html
          pages.py job_match   jobs.html
          profile  resume_svc  ...
          apps     app_svc
              │       │
              └───────┴──▶ JSONStore ──▶ app/data/*.json
```

---

## Project Structure

```
ai-job-hunter/
│
├── app/
│   ├── main.py                    # FastAPI app, startup, mounts
│   │
│   ├── routes/
│   │   ├── pages.py               # HTML page routes (GET /)
│   │   ├── auth.py                # /api/auth/signup, signin, logout
│   │   ├── jobs.py                # /api/jobs, /api/jobs/{id}, /api/jobs/analyze
│   │   ├── profile.py             # /api/profile, /api/resume/upload
│   │   └── applications.py        # /api/applications CRUD
│   │
│   ├── services/
│   │   ├── openai_service.py      # analyze_resume(), match_jobs(), generate_cover_letter()
│   │   ├── resume_service.py      # File parsing, text extraction
│   │   ├── job_matching_service.py# Local pre-filter + AI ranking
│   │   └── application_service.py # Application lifecycle management
│   │
│   ├── models/
│   │   ├── user.py                # Pydantic models for users
│   │   ├── job.py                 # Pydantic models for jobs
│   │   ├── resume.py              # Pydantic models for resumes/profiles
│   │   └── application.py         # Pydantic models for applications
│   │
│   ├── utils/
│   │   ├── json_store.py          # Reusable JSON file CRUD utility
│   │   ├── auth.py                # Session management, password hashing
│   │   └── file_parser.py         # PDF/DOCX/TXT text extraction
│   │
│   └── data/
│       ├── users.json             # User accounts
│       ├── jobs.json              # 150 dummy job listings
│       ├── resumes.json           # Parsed resume profiles
│       ├── applications.json      # Application records
│       └── preferences.json       # User job preferences
│
├── templates/
│   ├── base.html                  # Base layout with navbar, toasts
│   ├── index.html                 # Landing page
│   ├── signup.html                # Registration
│   ├── signin.html                # Login
│   ├── dashboard.html             # Post-login dashboard
│   ├── analyze.html               # Resume upload + preferences
│   ├── jobs.html                  # Job discovery (split layout)
│   ├── job_detail.html            # Single job view
│   ├── applications.html          # Application tracker
│   └── profile.html               # User profile editor
│
├── static/
│   ├── css/styles.css             # Custom CSS beyond Tailwind
│   ├── js/
│   │   ├── main.js                # Global utilities, toasts, navbar
│   │   ├── auth.js                # Signup/signin form handling
│   │   ├── analyze.js             # Resume upload + analysis flow
│   │   ├── jobs.js                # Job list + detail interaction
│   │   └── applications.js        # Application tracker UI
│   └── uploads/                   # Uploaded resume files
│
├── seed/
│   └── generate_jobs.py           # Script to regenerate jobs.json
│
├── docs/
│   ├── architecture.md            # Detailed architecture docs
│   ├── api.md                     # Full API reference
│   └── development.md             # Developer guide
│
├── requirements.txt
├── .env.example
├── .gitignore
├── CLAUDE.md                      # Instructions for Claude Code
├── agent.md                       # AI agent pipeline documentation
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/MaryamMumtaz-piaic/ai-job-hunter.git
cd ai-job-hunter

# Create virtual environment
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — Mac/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
# At minimum: set SECRET_KEY to any random string
# For AI features: add your OPENAI_API_KEY and set OPENAI_MOCK_MODE=false
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | *(required for real mode)* |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `OPENAI_MOCK_MODE` | Use mock AI responses | `true` |
| `SECRET_KEY` | Session signing key | `change-me-in-production` |

---

## Running the Application

```bash
uvicorn app.main:app --reload --port 8000
```

Then open your browser at: **http://localhost:8000**

On first run, if `app/data/jobs.json` is empty, the server auto-seeds 150 realistic dummy jobs.

---

## OpenAI Configuration

### Real Mode

Set your API key and disable mock mode:

```env
OPENAI_API_KEY=sk-...
OPENAI_MOCK_MODE=false
OPENAI_MODEL=gpt-4o-mini
```

### Mock Mode (default)

Works without any API key. Returns realistic deterministic data for:

- Resume analysis — returns a complete structured profile
- Job matching — returns ranked jobs with scores and reasoning
- Cover letter generation — returns a professional template letter

```env
OPENAI_MOCK_MODE=true
```

---

## API Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `POST` | `/api/auth/signup` | Register new user | No |
| `POST` | `/api/auth/signin` | Login | No |
| `POST` | `/api/auth/logout` | Logout | Yes |
| `GET` | `/api/user` | Get current user info | Yes |
| `GET` | `/api/profile` | Get user profile | Yes |
| `PUT` | `/api/profile` | Update user profile | Yes |
| `POST` | `/api/resume/upload` | Upload resume file | Yes |
| `POST` | `/api/resume/analyze` | AI-analyze uploaded resume | Yes |
| `GET` | `/api/jobs` | List all/filtered jobs | Yes |
| `GET` | `/api/jobs/{job_id}` | Get single job detail | Yes |
| `POST` | `/api/jobs/analyze` | Run AI job matching | Yes |
| `POST` | `/api/jobs/{job_id}/save` | Save/unsave a job | Yes |
| `POST` | `/api/applications` | Create application | Yes |
| `GET` | `/api/applications` | List user's applications | Yes |
| `GET` | `/api/applications/{id}` | Get application detail | Yes |
| `PUT` | `/api/applications/{id}` | Update application status | Yes |
| `POST` | `/api/cover-letter/generate` | Generate cover letter | Yes |

See [docs/api.md](docs/api.md) for full request/response schemas and examples.

---

## User Journey

```
LANDING PAGE  →  GET STARTED
                      │
                   SIGN UP
                      │
                   SIGN IN
                      │
                 DASHBOARD
                      │
             ANALYZE MY RESUME
                      │
          UPLOAD RESUME / PORTFOLIO
                      │
            AI RESUME ANALYSIS
                      │
            JOB PREFERENCES FORM
                      │
             [Analyze Matching Jobs]
                      │
           ┌──── AI MATCHING AGENT ────┐
           │                           │
       SAVE JOB                   VIEW JOB DETAIL
                                       │
                                    [Apply]
                                       │
                              APPLICATION PREVIEW
                              (auto-filled from profile)
                                       │
                              GENERATE COVER LETTER
                                       │
                                  HUMAN REVIEW
                              (resume + cover letter
                               + candidate info)
                                       │
                              [Approve & Submit]
                                       │
                            APPLICATION RECORDED
                                       │
                            APPLICATION TRACKER
```

---

## MVP Limitations

This is a simulation and local development tool. It intentionally does NOT:

- Scrape real job boards (LinkedIn, Indeed, Glassdoor, etc.)
- Submit applications to external websites
- Send emails or notifications
- Connect to any external API beyond OpenAI
- Store data in a production database
- Support multiple concurrent users at scale
- Implement OAuth or social login
- Perform automated browser actions on job sites
- Bypass CAPTCHAs or login walls

---

## Future Improvements

1. **Real job ingestion** — Integrate job board APIs (LinkedIn Jobs API, Adzuna, RapidAPI)
2. **PostgreSQL persistence** — Replace JSON files with a proper database for multi-user support
3. **Email notifications** — Send application status updates via email
4. **Resume versioning** — Track multiple resume versions and which was used per application
5. **Interview scheduler** — Calendar integration for interview tracking
6. **Analytics dashboard** — Response rates, interview-to-offer ratios, skill demand trends
7. **Browser automation** — Playwright-based auto-fill for supported job boards (with user oversight)
8. **Vector search** — Embed jobs and resumes for semantic similarity matching
9. **Multi-language support** — Internationalization for global job markets
10. **Mobile app** — React Native companion for on-the-go application management

---

## License

MIT License — Copyright (c) 2026 Maryam Mumtaz

See [LICENSE](LICENSE) for full text.

---

## Author

**Maryam Mumtaz**
- Portfolio: [maryam-piaic.vercel.app](https://maryam-piaic.vercel.app)
- GitHub: [@MaryamMumtaz-piaic](https://github.com/MaryamMumtaz-piaic)
- LinkedIn: [maryammumtaz-](https://www.linkedin.com/in/maryammumtaz-)
- Email: maryamqureshimumtazm.a@gmail.com
