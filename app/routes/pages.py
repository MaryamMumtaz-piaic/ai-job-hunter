from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.json_store import JSONStore
from app.utils.auth import get_current_user
from collections import Counter
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _get_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    users = JSONStore("app/data/users.json")
    return users.find_by_id(user_id)


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = _get_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    user_id = user["id"]
    apps_store = JSONStore("app/data/applications.json")
    resumes_store = JSONStore("app/data/resumes.json")
    prefs_store = JSONStore("app/data/preferences.json")
    jobs_store = JSONStore("app/data/jobs.json")

    all_apps = apps_store.find(lambda a: a.get("user_id") == user_id)
    status_counts = Counter(a.get("status", "Draft") for a in all_apps)
    saved_jobs = user.get("saved_jobs", [])

    recent_apps = sorted(all_apps, key=lambda a: a.get("created_at", ""), reverse=True)[:5]

    # Enrich recent apps with job info
    for app in recent_apps:
        job = jobs_store.find_by_id(app.get("job_id", ""))
        app["job_info"] = job or {}

    # Recommended jobs from last analysis
    matched_jobs = []
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user_id)
    if resume_data:
        latest_resume = resume_data[-1]
        matched = latest_resume.get("matched_jobs", [])[:5]
        for m in matched:
            job_id_key = m.get("job_id") or m.get("id", "")
            job = jobs_store.find_by_id(job_id_key)
            if job:
                job["match_score"] = m.get("match_score", 0)
                job["match_reason"] = m.get("match_reason", "")
                matched_jobs.append(job)

    stats = {
        "total_applications": len(all_apps),
        "pending": status_counts.get("Pending Approval", 0) + status_counts.get("Draft", 0),
        "submitted": status_counts.get("Submitted", 0),
        "saved_jobs": len(saved_jobs),
        "matched_jobs": len(matched_jobs),
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "recent_apps": recent_apps,
        "recommended_jobs": matched_jobs,
    })


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    resumes_store = JSONStore("app/data/resumes.json")
    prefs_store = JSONStore("app/data/preferences.json")

    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    latest_resume = resume_data[-1] if resume_data else None

    prefs = prefs_store.find(lambda p: p.get("user_id") == user["id"])
    latest_prefs = prefs[-1] if prefs else None

    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "user": user,
        "resume": latest_resume,
        "preferences": latest_prefs,
    })


@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    resumes_store = JSONStore("app/data/resumes.json")
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    latest_resume = resume_data[-1] if resume_data else None

    has_analysis = latest_resume and bool(latest_resume.get("matched_jobs"))

    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "user": user,
        "has_analysis": has_analysis,
    })


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail_page(request: Request, job_id: str):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    jobs_store = JSONStore("app/data/jobs.json")
    job = jobs_store.find_by_id(job_id)
    if not job:
        return RedirectResponse("/jobs", status_code=302)

    # Attach match info if available
    resumes_store = JSONStore("app/data/resumes.json")
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    if resume_data:
        latest_resume = resume_data[-1]
        for m in latest_resume.get("matched_jobs", []):
            if m.get("job_id") == job_id:
                job["match_score"] = m.get("match_score", 0)
                job["match_reason"] = m.get("match_reason", "")
                job["matched_skills"] = m.get("matched_skills", [])
                job["missing_skills"] = m.get("missing_skills", [])
                break

    saved_jobs = user.get("saved_jobs", [])
    job["is_saved"] = job_id in saved_jobs

    return templates.TemplateResponse("job_detail.html", {
        "request": request,
        "user": user,
        "job": job,
    })


@router.get("/applications", response_class=HTMLResponse)
async def applications_page(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    apps_store = JSONStore("app/data/applications.json")
    jobs_store = JSONStore("app/data/jobs.json")

    all_apps = apps_store.find(lambda a: a.get("user_id") == user["id"])
    all_apps = sorted(all_apps, key=lambda a: a.get("created_at", ""), reverse=True)

    for app in all_apps:
        job = jobs_store.find_by_id(app.get("job_id", ""))
        app["job_info"] = job or {}

    return templates.TemplateResponse("applications.html", {
        "request": request,
        "user": user,
        "applications": all_apps,
    })


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/signin", status_code=302)

    resumes_store = JSONStore("app/data/resumes.json")
    prefs_store = JSONStore("app/data/preferences.json")

    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    latest_resume = resume_data[-1] if resume_data else None

    prefs = prefs_store.find(lambda p: p.get("user_id") == user["id"])
    latest_prefs = prefs[-1] if prefs else None

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "resume": latest_resume,
        "preferences": latest_prefs,
    })


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = _get_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request, "user": None})


@router.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    user = _get_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("signin.html", {"request": request, "user": None})
