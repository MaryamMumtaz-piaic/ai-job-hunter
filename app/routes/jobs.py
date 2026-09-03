from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.json_store import JSONStore
from app.utils.auth import get_current_user
from datetime import datetime
import uuid

router = APIRouter()


@router.get("")
async def list_jobs(
    request: Request,
    search: str = "",
    work_mode: str = "",
    employment_type: str = "",
    country: str = "",
    experience_level: str = "",
    page: int = 1,
    limit: int = 20,
):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jobs_store = JSONStore("app/data/jobs.json")
    jobs = jobs_store.read()

    # Apply filters
    if search:
        search_lower = search.lower()
        jobs = [
            j for j in jobs
            if search_lower in j.get("title", "").lower()
            or search_lower in j.get("company", "").lower()
            or search_lower in j.get("description", "").lower()
            or any(search_lower in s.lower() for s in j.get("skills", []))
        ]
    if work_mode and work_mode != "Any":
        jobs = [j for j in jobs if j.get("work_mode", "").lower() == work_mode.lower()]
    if employment_type and employment_type != "Any":
        jobs = [j for j in jobs if j.get("employment_type", "").lower() == employment_type.lower()]
    if country and country != "Any":
        jobs = [j for j in jobs if j.get("country", "").lower() == country.lower()]
    if experience_level and experience_level != "Any":
        jobs = [j for j in jobs if j.get("experience_level", "").lower() == experience_level.lower()]

    total = len(jobs)
    start = (page - 1) * limit
    paginated = jobs[start:start + limit]

    saved_jobs = user.get("saved_jobs", [])

    # Attach match scores from latest analysis
    resumes_store = JSONStore("app/data/resumes.json")
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    match_map = {}
    if resume_data:
        latest = resume_data[-1]
        for m in latest.get("matched_jobs", []):
            match_map[m.get("job_id")] = m

    for job in paginated:
        job["is_saved"] = job["id"] in saved_jobs
        if job["id"] in match_map:
            job["match_score"] = match_map[job["id"]].get("match_score", 0)
            job["match_reason"] = match_map[job["id"]].get("match_reason", "")

    return JSONResponse({
        "success": True,
        "jobs": paginated,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    })


@router.get("/saved")
async def get_saved_jobs(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jobs_store = JSONStore("app/data/jobs.json")
    saved_ids = user.get("saved_jobs", [])
    saved = [jobs_store.find_by_id(jid) for jid in saved_ids]
    saved = [j for j in saved if j]

    return JSONResponse({"success": True, "jobs": saved})


@router.get("/{job_id}")
async def get_job(request: Request, job_id: str):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jobs_store = JSONStore("app/data/jobs.json")
    job = jobs_store.find_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    saved_jobs = user.get("saved_jobs", [])
    job["is_saved"] = job_id in saved_jobs

    resumes_store = JSONStore("app/data/resumes.json")
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    if resume_data:
        latest = resume_data[-1]
        for m in latest.get("matched_jobs", []):
            if m.get("job_id") == job_id:
                job["match_score"] = m.get("match_score", 0)
                job["match_reason"] = m.get("match_reason", "")
                job["matched_skills"] = m.get("matched_skills", [])
                job["missing_skills"] = m.get("missing_skills", [])
                break

    return JSONResponse({"success": True, "job": job})


@router.post("/analyze")
async def analyze_jobs(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()

        resumes_store = JSONStore("app/data/resumes.json")
        prefs_store = JSONStore("app/data/preferences.json")

        resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
        prefs_data = prefs_store.find(lambda p: p.get("user_id") == user["id"])

        if not resume_data:
            return JSONResponse({"success": False, "message": "No resume found. Please upload and analyze your resume first."}, status_code=400)

        latest_resume = resume_data[-1]
        latest_prefs = prefs_data[-1] if prefs_data else {}

        from app.services.job_matching_service import run_matching
        matched = run_matching(user["id"], latest_prefs or {})

        # Save matched jobs to resume record
        resumes_store.update(latest_resume["id"], {"matched_jobs": matched})

        jobs_store = JSONStore("app/data/jobs.json")
        result_jobs = []
        for m in matched[:50]:
            job = jobs_store.find_by_id(m.get("job_id", ""))
            if job:
                job["match_score"] = m.get("match_score", 0)
                job["match_reason"] = m.get("match_reason", "")
                job["matched_skills"] = m.get("matched_skills", [])
                job["missing_skills"] = m.get("missing_skills", [])
                job["is_saved"] = m.get("job_id") in user.get("saved_jobs", [])
                result_jobs.append(job)

        return JSONResponse({
            "success": True,
            "jobs": result_jobs,
            "total": len(result_jobs),
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "message": "Job analysis failed. Please try again."}, status_code=500)


@router.post("/{job_id}/save")
async def toggle_save_job(request: Request, job_id: str):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jobs_store = JSONStore("app/data/jobs.json")
    job = jobs_store.find_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    users_store = JSONStore("app/data/users.json")
    saved_jobs = user.get("saved_jobs", [])

    if job_id in saved_jobs:
        saved_jobs.remove(job_id)
        saved = False
    else:
        saved_jobs.append(job_id)
        saved = True

    users_store.update(user["id"], {"saved_jobs": saved_jobs})
    return JSONResponse({"success": True, "saved": saved, "message": "Job saved" if saved else "Job removed from saved"})
