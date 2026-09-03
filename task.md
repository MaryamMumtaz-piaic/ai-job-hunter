# AI Job Hunter MVP

## Complete Implementation Prompt

You are an expert full-stack engineer. Build a complete, polished **AI Job Hunter MVP** as a local web application.

The application is an AI-powered job discovery and application assistant. It should allow a user to create an account, upload a resume/portfolio, define job preferences, analyze matching jobs from a local dummy dataset, review jobs, generate AI cover letters, and manually approve applications.

This is an **MVP**, not a production job-scraping platform. Do not over-engineer it.

---

# 1. Core Technology Requirements

Use exactly this architecture:

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* OpenAI Python SDK

### Frontend

* HTML
* Tailwind CSS
* Vanilla JavaScript
* Jinja2 templates

Do NOT use:

* React
* Next.js
* Vue
* Angular
* separate frontend server
* Node.js frontend
* unnecessary frontend frameworks

The FastAPI application must serve the entire frontend.

The final application must run with:

```bash
uvicorn app.main:app --reload --port 8000
```

Then the complete application should be accessible at:

```text
http://localhost:8000
```

There must be no separate frontend development server.

---

# 2. Main Architecture

Use a clean structure similar to:

```text
ai-job-hunter/
│
├── app/
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── pages.py
│   │   ├── auth.py
│   │   ├── jobs.py
│   │   ├── profile.py
│   │   └── applications.py
│   │
│   ├── services/
│   │   ├── openai_service.py
│   │   ├── resume_service.py
│   │   ├── job_matching_service.py
│   │   └── application_service.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   └── application.py
│   │
│   ├── utils/
│   │   ├── json_store.py
│   │   ├── auth.py
│   │   └── file_parser.py
│   │
│   └── data/
│       ├── users.json
│       ├── jobs.json
│       ├── resumes.json
│       ├── applications.json
│       └── preferences.json
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── signup.html
│   ├── signin.html
│   ├── dashboard.html
│   ├── analyze.html
│   ├── jobs.html
│   ├── job_detail.html
│   ├── applications.html
│   └── profile.html
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── main.js
│   │   ├── auth.js
│   │   ├── analyze.js
│   │   ├── jobs.js
│   │   └── applications.js
│   └── uploads/
│
├── seed/
│   └── generate_jobs.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

You may adjust the structure slightly if there is a better clean implementation, but keep the architecture simple.

---

# 3. FastAPI Must Serve Everything

FastAPI must:

* mount `/static`
* serve Jinja2 templates
* serve homepage
* serve authentication pages
* serve dashboard
* serve job pages
* serve application pages
* expose API endpoints where JavaScript needs asynchronous operations

Example:

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
```

The user should only need to run:

```bash
uvicorn app.main:app --reload --port 8000
```

No npm installation should be required.

---

# 4. Homepage

Create a premium modern landing page.

The homepage flow is:

```text
Navbar
Hero
How It Works
Features
Job Discovery Preview
AI Workflow
CTA
Footer
```

## Navbar

Left:

```text
AI Job Hunter
```

Right:

```text
Home
How It Works
Features
Sign In
Get Started
```

When the user is authenticated:

```text
Home
Jobs
Applications
Profile
Dashboard
[User Avatar]
```

Hide:

```text
Sign In
Get Started
```

when authenticated.

---

# 5. Visual Design

The UI is extremely important.

Make the interface look like a polished modern SaaS product.

Use:

* clean white/light background
* subtle gradients
* rounded cards
* soft borders
* modern typography
* subtle shadows
* professional spacing
* responsive layout
* excellent empty states
* loading states
* hover states
* transitions
* polished modals
* toast notifications

Avoid:

* ugly default HTML forms
* generic bootstrap appearance
* excessive gradients
* excessive animations
* huge unnecessary cards
* overly colorful dashboards
* clutter
* unnecessary UI components

The application should feel like a real modern product.

---

# 6. Authentication

Implement:

```text
/signup
/signin
/logout
```

Registration fields:

```text
Full Name
Email
Password
Confirm Password
```

Login:

```text
Email
Password
```

For this MVP, store users locally in:

```text
app/data/users.json
```

Use secure password hashing such as `passlib`/bcrypt or another appropriate local password hashing implementation.

Do NOT store plaintext passwords.

Use a simple session mechanism.

The user must remain authenticated while navigating the application.

---

# 7. Signup Flow

User visits:

```text
/
```

Clicks:

```text
Get Started
```

Redirect:

```text
/signup
```

After successful signup:

```text
/signup
        ↓
/signin
```

After successful signin:

```text
/signin
        ↓
/dashboard
```

---

# 8. Dashboard

After login, show a personalized dashboard.

Example:

```text
Good morning, Muhammad

Find your next opportunity.

[Analyze My Resume]
```

Stats:

```text
Matched Jobs
Applications
Pending
Saved Jobs
```

Recent applications:

```text
Company
Position
Date
Status
```

Recommended jobs:

```text
Job
Company
Location
Match %
Apply
```

The dashboard must use the currently authenticated user's data.

---

# 9. Resume / Portfolio Analysis

When the user clicks:

```text
Analyze My Resume
```

open a polished modal or dedicated analysis page.

The user can upload:

```text
PDF
DOCX
TXT
```

Also allow:

```text
Portfolio / CV
```

if appropriate.

The UI should clearly show:

```text
Upload Resume
Upload Portfolio
```

Allow the user to upload one or both.

After upload, display:

```text
Resume uploaded ✓
Portfolio uploaded ✓
```

---

# 10. Resume Parsing

After upload, extract the relevant text from the document.

Use OpenAI to analyze the resume.

Extract structured information such as:

```json
{
  "name": "",
  "email": "",
  "summary": "",
  "skills": [],
  "experience": [],
  "education": [],
  "years_of_experience": 0,
  "job_titles": [],
  "industries": [],
  "technologies": []
}
```

Do not invent information.

If something is missing, return an empty value.

Store the extracted profile locally.

---

# 11. Job Preferences

After resume analysis, ask the user what kind of job they want.

Create a polished preference form.

Fields:

### Job Type

Allow:

```text
Full-time
Part-time
Contract
Internship
Freelance
```

### Work Mode

Allow:

```text
Remote
Hybrid
On-site
Any
```

### Desired Job Titles

Example:

```text
AI Engineer
Full Stack Developer
Backend Engineer
Software Engineer
```

Allow multiple values.

### Country

Example:

```text
Pakistan
United States
United Kingdom
Canada
Germany
Australia
Any
```

### City

Optional.

### Minimum Salary

Optional.

### Maximum Salary

Optional.

### Experience Level

```text
Intern
Entry Level
Mid Level
Senior
Lead
Any
```

### Employment Preferences

Allow:

```text
Startup
Enterprise
Agency
Any
```

### Skills

Automatically prefill skills detected from the resume.

Allow the user to edit them.

---

# 12. Analyze Button

After preferences are completed:

```text
[Analyze Matching Jobs]
```

When clicked, show a full-screen or large modal loading experience.

Do NOT immediately show results.

Simulate a realistic analysis process lasting approximately 30-90 seconds.

The loading UI should display stages such as:

```text
✓ Resume analyzed
✓ Skills extracted
✓ Job preferences processed
✓ Job database scanned
● Matching opportunities
○ Ranking jobs
○ Preparing recommendations
```

The stages should visually update.

Do not make the UI appear frozen.

The backend may process the matching quickly, while the frontend presents a realistic analysis experience.

Do not artificially block the backend for 90 seconds.

---

# 13. Dummy Job Dataset

Create a local dataset containing approximately:

```text
100-200 jobs
```

Store it in:

```text
app/data/jobs.json
```

These must be realistic dummy jobs.

Do NOT scrape real websites.

Each job should contain:

```json
{
  "id": "JOB-001",
  "title": "AI Engineer",
  "company": "Nova Labs",
  "location": "Remote",
  "country": "United States",
  "work_mode": "Remote",
  "employment_type": "Full-time",
  "experience_level": "Mid Level",
  "salary_min": 85000,
  "salary_max": 120000,
  "currency": "USD",
  "description": "...",
  "requirements": [],
  "skills": [],
  "benefits": [],
  "posted_date": "",
  "company_description": "",
  "industry": "Technology"
}
```

Create enough diversity across:

* AI
* software engineering
* frontend
* backend
* full-stack
* DevOps
* data
* cybersecurity
* product
* design
* marketing
* finance
* healthcare
* startups
* enterprise

Include different:

* countries
* salary ranges
* work modes
* seniority levels
* companies

The dataset must feel realistic.

---

# 14. Job Matching Agent

This is one of the important AI components.

Use OpenAI.

The matching agent receives:

```text
Candidate Profile
+
Candidate Skills
+
Experience
+
Desired Job Titles
+
Location Preferences
+
Work Mode
+
Salary Preferences
+
Job Dataset
```

It should determine which jobs are relevant.

For each matching job, calculate or return:

```text
match_score
```

Example:

```text
94%
87%
81%
76%
```

The AI should explain the match.

Example:

```text
Strong match because your Python, FastAPI and AI agent experience
closely align with the required backend and AI engineering skills.
```

Also identify:

```text
Matched Skills
Missing Skills
Why This Job Fits
```

Important:

Do not blindly send all 200 jobs into one enormous OpenAI request if it causes unnecessary token usage.

Implement a lightweight local pre-filter first using:

* job title
* skills
* location
* work mode
* experience
* salary

Then use OpenAI to rank/analyze the relevant subset.

This is an MVP, so optimize reasonably without overengineering.

---

# 15. Jobs Results UI

After analysis, show the jobs page.

Layout:

```text
┌─────────────────────────────────────────────┐
│ Search / Filters                            │
├───────────────┬─────────────────────────────┤
│               │                             │
│ Job List      │ Selected Job               │
│               │                             │
│ AI Engineer   │ AI Engineer                │
│ 94% Match     │ Nova Labs                  │
│               │ Remote                     │
│ Full-time     │ $90k - $120k               │
│               │                             │
│ Backend Eng.  │ [Apply] [Save]             │
│ 88% Match     │                             │
│               │                             │
└───────────────┴─────────────────────────────┘
```

Desktop:

```text
Left = job list
Right = job detail
```

Mobile:

```text
Job list
↓
Job detail
```

---

# 16. Job Card

Each job card should show:

```text
Company Logo / Initial
Job Title
Company
Location
Work Mode
Salary
Employment Type
Match Score
```

Example:

```text
Nova Labs

AI Engineer
Remote • United States

$90K - $120K
Full-time

94% Match

[View Job]
```

Use dummy company logos/initials.

Do not depend on external logo APIs.

---

# 17. Job Detail

Show:

```text
Job Title
Company
Location
Salary
Work Mode
Employment Type
Experience
```

Then:

```text
About the Role
Requirements
Responsibilities
Benefits
Why You're a Match
Skill Match
Potential Gaps
```

Actions:

```text
[Apply]
[Save Job]
[Generate Cover Letter]
```

---

# 18. Apply Workflow

When the user clicks:

```text
Apply
```

DO NOT automatically submit anything to a real external website.

This is only an MVP simulation.

Open an application workflow.

Show:

```text
Application Preview
```

Automatically populate available candidate information from the user's profile:

```text
Name
Email
Phone
Location
Resume
Portfolio
LinkedIn
GitHub
Skills
Experience
```

The user should be able to review/edit the information.

---

# 19. Cover Letter Generation

Add:

```text
Generate Cover Letter
```

Use OpenAI.

Inputs:

```text
Candidate Resume/Profile
+
Job Description
+
Company
+
Job Title
```

Generate a professional personalized cover letter.

The user should be able to:

```text
Generate
Regenerate
Edit
Copy
Save
```

Store generated cover letters locally.

---

# 20. Human Approval Workflow

This is extremely important.

Never pretend that a real job application was submitted.

Before final application:

```text
Review Application
```

Show:

```text
Resume
Candidate Information
Cover Letter
Job Information
```

Then:

```text
[Approve & Submit]
```

The user explicitly approves.

After approval, simulate submission.

Show:

```text
Application submitted successfully
```

The application status becomes:

```text
Submitted
```

Do NOT actually send applications to external job websites.

---

# 21. Application Tracking

Create:

```text
/applications
```

Show all applications belonging to the authenticated user.

Statuses:

```text
Draft
Pending Approval
Approved
Submitted
Interview
Rejected
Offer
```

For the MVP, the initial workflow is:

```text
Draft
↓
Pending Approval
↓
Submitted
```

Allow the user to manually update status later.

Application card:

```text
AI Engineer
Nova Labs

Applied:
September 3, 2026

Status:
Submitted

[View Application]
```

---

# 22. Homepage Profile Indicator

Once logged in, the navbar should display:

```text
Avatar
Muhammad
```

Clicking it should show:

```text
Dashboard
Profile
Applications
Logout
```

The homepage/dashboard should also show a small application summary:

```text
Applications
12

Pending
4

Submitted
8
```

---

# 23. Profile Page

Create:

```text
/profile
```

Sections:

```text
Personal Information
Professional Summary
Skills
Experience
Education
Resume
Portfolio
Job Preferences
```

Allow editing.

The resume-derived information should be editable.

---

# 24. Local JSON Persistence

For this MVP, do NOT introduce PostgreSQL.

Use JSON files.

Example:

```text
users.json
jobs.json
resumes.json
applications.json
preferences.json
```

Create a small reusable JSON storage utility.

It should safely:

```text
read()
write()
find()
find_by_id()
update()
append()
```

Use proper file handling.

Avoid duplicating JSON manipulation logic throughout routes.

---

# 25. OpenAI Integration

Create:

```text
services/openai_service.py
```

Use environment variable:

```text
OPENAI_API_KEY=
```

Create separate functions for:

```python
analyze_resume()
match_jobs()
generate_cover_letter()
```

Use structured JSON responses wherever possible.

The OpenAI integration should fail gracefully.

If the API key is missing:

* show a clear configuration message
* do not crash the entire application

For local UI development, provide a mock/fallback mode.

Example:

```text
OPENAI_MOCK_MODE=true
```

When mock mode is enabled, return deterministic realistic data.

---

# 26. Agent Architecture

Do not build a huge autonomous multi-agent framework.

Use a simple agent/service architecture.

Conceptually:

```text
User
 │
 ▼
Resume Analyzer
 │
 ▼
Job Preference Analyzer
 │
 ▼
Job Matching Agent
 │
 ▼
Job Ranking
 │
 ▼
User Review
 │
 ▼
Cover Letter Agent
 │
 ▼
Human Approval
 │
 ▼
Application Record
```

The important thing is to make the architecture extensible.

---

# 27. API Endpoints

Implement clean endpoints approximately like:

```text
POST   /api/auth/signup
POST   /api/auth/signin
POST   /api/auth/logout

GET    /api/user
GET    /api/profile
PUT    /api/profile

POST   /api/resume/upload
POST   /api/resume/analyze

GET    /api/jobs
GET    /api/jobs/{job_id}

POST   /api/jobs/analyze
POST   /api/jobs/{job_id}/save

POST   /api/applications
GET    /api/applications
GET    /api/applications/{application_id}
PUT    /api/applications/{application_id}

POST   /api/cover-letter/generate
```

Use appropriate request/response models.

---

# 28. Security Basics

Even though this is an MVP:

* hash passwords
* validate uploaded files
* limit upload size
* sanitize filenames
* do not expose `.env`
* do not expose private JSON files through static routes
* validate user ownership before accessing applications/resumes
* do not expose other users' data
* never put API keys in frontend JavaScript

---

# 29. Loading Experience

The analysis experience is a major part of the product.

Create a polished loader.

Example:

```text
Analyzing your career profile

✓ Reading resume
✓ Extracting skills
✓ Understanding experience
✓ Applying job preferences
● Finding matching opportunities
○ Ranking jobs
○ Preparing recommendations

This may take a moment...
```

Use animated progress indicators.

The UI should feel intentional, not like a random spinner.

---

# 30. Toast Notifications

Implement lightweight toast notifications for:

```text
Account created
Signed in
Resume uploaded
Resume analyzed
Preferences saved
Job saved
Cover letter generated
Application approved
Application submitted
```

---

# 31. Empty States

Every major page needs a proper empty state.

Examples:

Applications:

```text
No applications yet

Start exploring opportunities that match your profile.

[Find Jobs]
```

Saved Jobs:

```text
No saved jobs

Save interesting opportunities and come back later.
```

Resume:

```text
No resume uploaded

Upload your resume to start finding better matches.

[Upload Resume]
```

---

# 32. Error Handling

Never show raw Python exceptions to the user.

Use friendly messages.

Example:

```text
Something went wrong while analyzing your resume.

Please try again.
```

Log the actual error server-side.

---

# 33. Responsive Design

The application must work on:

```text
Desktop
Laptop
Tablet
Mobile
```

The jobs split layout must transform correctly on smaller screens.

Do not simply shrink desktop UI.

Actually redesign the layout for mobile.

---

# 34. Demo Data

When the application starts for the first time:

If:

```text
jobs.json
```

doesn't exist or is empty:

Generate/load the predefined 100-200 dummy jobs.

Also include several demo jobs specifically suitable for:

```text
AI Engineer
AI Agent Engineer
Full Stack Developer
Python Developer
Backend Engineer
Frontend Engineer
Software Engineer
```

This ensures the resume matching experience looks good during demonstration.

---

# 35. No Real External Job Submission

This must remain an MVP.

Do NOT implement:

* LinkedIn automation
* Indeed automation
* browser automation
* CAPTCHA bypassing
* external account login
* real job scraping
* real application submission

Applications should only be simulated and recorded locally.

The UI can make the workflow look complete, but it must clearly be a simulated application workflow.

---

# 36. README

Create a professional README containing:

```text
Project Overview
Features
Architecture
Tech Stack
Project Structure
Installation
Environment Variables
Running the Application
OpenAI Configuration
Mock Mode
API Endpoints
MVP Limitations
Future Improvements
```

Installation should be straightforward.

Example:

```bash
python -m venv .venv
```

Then activate the environment and:

```bash
pip install -r requirements.txt
```

Then:

```bash
uvicorn app.main:app --reload --port 8000
```

---

# 37. Environment Variables

Create:

```text
.env.example
```

with:

```env
OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_MOCK_MODE=true
SECRET_KEY=
```

Never hardcode secrets.

---

# 38. Important Implementation Rule

Do not build unnecessary infrastructure.

This is an MVP.

Prioritize:

1. Excellent UI
2. Correct navigation
3. Working authentication
4. Resume upload
5. Resume analysis
6. Job preference collection
7. Dummy job dataset
8. AI job matching
9. Job results
10. Cover-letter generation
11. Human approval
12. Application tracking
13. Local JSON persistence

Do NOT spend time implementing production-scale infrastructure.

---

# 39. User Journey

The complete intended experience is:

```text
LANDING PAGE
     │
     ▼
GET STARTED
     │
     ▼
SIGN UP
     │
     ▼
SIGN IN
     │
     ▼
DASHBOARD
     │
     ▼
ANALYZE MY RESUME
     │
     ▼
UPLOAD RESUME / PORTFOLIO
     │
     ▼
AI RESUME ANALYSIS
     │
     ▼
JOB PREFERENCES
     │
     ▼
ANALYZE JOBS
     │
     ▼
AI MATCHING AGENT
     │
     ▼
MATCHED JOBS
     │
     ├──────────────┐
     ▼              ▼
SAVE JOB        APPLY
                    │
                    ▼
             APPLICATION PREVIEW
                    │
                    ▼
             GENERATE COVER LETTER
                    │
                    ▼
               HUMAN REVIEW
                    │
                    ▼
             APPROVE & SUBMIT
                    │
                    ▼
              APPLICATION TRACKER
```

---

# 40. Final Quality Requirement

Before considering the project complete, test the entire flow from a clean installation:

```text
Homepage
→ Signup
→ Signin
→ Dashboard
→ Resume Upload
→ Resume Analysis
→ Preferences
→ Job Analysis
→ Job Results
→ Job Details
→ Apply
→ Cover Letter Generation
→ Human Approval
→ Application Submission
→ Application Tracker
→ Profile
→ Logout
```

Fix broken routes, JavaScript errors, template errors, missing assets, and state-management issues.

Do not leave placeholder buttons that do nothing.

Every visible primary button must either work or be explicitly marked as an MVP/demo feature.

The final result should feel like a **complete AI Job Hunter product**, even though the job database and application submission are simulated.

---

# 41. Development Approach

Build this incrementally:

### Phase 1

Project setup + FastAPI + Jinja + Tailwind + base layout.

### Phase 2

Landing page + authentication.

### Phase 3

Dashboard + profile.

### Phase 4

Resume/portfolio upload + extraction.

### Phase 5

OpenAI resume analysis.

### Phase 6

Job dataset + preference system.

### Phase 7

Job matching agent + analysis UI.

### Phase 8

Job discovery/results/detail UI.

### Phase 9

Application workflow.

### Phase 10

OpenAI cover-letter generation.

### Phase 11

Human approval + application tracking.

### Phase 12

Responsive polish + error handling + README.

Do not skip directly to a complicated architecture.

---

# 42. Critical Instruction

**Build the actual application, not just a mockup.**

The UI must be functional.

The backend must be functional.

The authentication must work.

JSON persistence must work.

Resume upload must work.

OpenAI integration must work when configured.

Mock mode must work without an API key.

Job matching must work against the local dataset.

Cover-letter generation must work.

Application approval must work.

Application tracking must work.

Everything should run from a single FastAPI server at:

```text
http://localhost:8000
```

Do not introduce React, Next.js, Node.js, PostgreSQL, Docker, Redis, Celery, or other infrastructure unless absolutely necessary.

Keep the implementation focused, clean, modular, and easy to extend later.
