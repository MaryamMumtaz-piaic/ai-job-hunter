from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.json_store import JSONStore
from app.utils.auth import get_current_user
from datetime import datetime
import uuid

router = APIRouter()

VALID_STATUSES = ["Draft", "Pending Approval", "Approved", "Submitted", "Interview", "Rejected", "Offer"]


@router.post("")
async def create_application(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        job_id = body.get("job_id")
        if not job_id:
            return JSONResponse({"success": False, "message": "job_id is required"}, status_code=400)

        jobs_store = JSONStore("app/data/jobs.json")
        job = jobs_store.find_by_id(job_id)
        if not job:
            return JSONResponse({"success": False, "message": "Job not found"}, status_code=404)

        apps_store = JSONStore("app/data/applications.json")
        existing = apps_store.find(lambda a: a.get("user_id") == user["id"] and a.get("job_id") == job_id)
        if existing:
            return JSONResponse({"success": True, "application": existing[0], "message": "Application already exists"})

        resumes_store = JSONStore("app/data/resumes.json")
        resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
        latest_resume = resume_data[-1] if resume_data else {}

        app_id = str(uuid.uuid4())
        application = {
            "id": app_id,
            "user_id": user["id"],
            "job_id": job_id,
            "status": "Draft",
            "candidate_info": {
                "full_name": user.get("full_name", ""),
                "email": user.get("email", ""),
                "phone": user.get("phone", ""),
                "location": user.get("location", ""),
                "linkedin": user.get("linkedin", ""),
                "github": user.get("github", ""),
                "resume_file": user.get("resume_file", ""),
                "portfolio_file": user.get("portfolio_file", ""),
                "skills": latest_resume.get("skills", []),
                "summary": latest_resume.get("summary", ""),
            },
            "cover_letter": body.get("cover_letter", ""),
            "match_score": body.get("match_score", 0),
            "notes": "",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "submitted_at": None,
        }

        apps_store.append(application)
        return JSONResponse({"success": True, "application": application}, status_code=201)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "message": "Failed to create application"}, status_code=500)


@router.get("")
async def list_applications(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    apps_store = JSONStore("app/data/applications.json")
    jobs_store = JSONStore("app/data/jobs.json")

    apps = apps_store.find(lambda a: a.get("user_id") == user["id"])
    apps = sorted(apps, key=lambda a: a.get("created_at", ""), reverse=True)

    for app in apps:
        job = jobs_store.find_by_id(app.get("job_id", ""))
        app["job_info"] = job or {}

    return JSONResponse({"success": True, "applications": apps})


@router.get("/{application_id}")
async def get_application(request: Request, application_id: str):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    apps_store = JSONStore("app/data/applications.json")
    app = apps_store.find_by_id(application_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    jobs_store = JSONStore("app/data/jobs.json")
    job = jobs_store.find_by_id(app.get("job_id", ""))
    app["job_info"] = job or {}

    return JSONResponse({"success": True, "application": app})


@router.put("/{application_id}")
async def update_application(request: Request, application_id: str):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    apps_store = JSONStore("app/data/applications.json")
    app = apps_store.find_by_id(application_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        body = await request.json()
        allowed_updates = ["cover_letter", "candidate_info", "notes", "status"]
        updates = {k: v for k, v in body.items() if k in allowed_updates}

        if "status" in updates and updates["status"] not in VALID_STATUSES:
            return JSONResponse({"success": False, "message": f"Invalid status. Valid: {VALID_STATUSES}"}, status_code=400)

        updates["updated_at"] = datetime.utcnow().isoformat()
        apps_store.update(application_id, updates)

        return JSONResponse({"success": True, "message": "Application updated"})
    except Exception as e:
        return JSONResponse({"success": False, "message": "Failed to update application"}, status_code=500)


@router.post("/{application_id}/approve")
async def approve_application(request: Request, application_id: str):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    apps_store = JSONStore("app/data/applications.json")
    app = apps_store.find_by_id(application_id)

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    now = datetime.utcnow().isoformat()
    apps_store.update(application_id, {
        "status": "Submitted",
        "submitted_at": now,
        "updated_at": now,
    })

    return JSONResponse({"success": True, "message": "Application approved and submitted successfully!"})


@router.post("/cover-letter/generate")
async def generate_cover_letter(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        job_id = body.get("job_id")
        application_id = body.get("application_id")

        jobs_store = JSONStore("app/data/jobs.json")
        job = jobs_store.find_by_id(job_id) if job_id else None

        resumes_store = JSONStore("app/data/resumes.json")
        resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
        latest_resume = resume_data[-1] if resume_data else {}

        from app.services.openai_service import generate_cover_letter as ai_generate
        cover_letter = ai_generate(
            candidate_profile=latest_resume,
            candidate_name=user.get("full_name", ""),
            job=job or {},
        )

        if application_id:
            apps_store = JSONStore("app/data/applications.json")
            existing_app = apps_store.find_by_id(application_id)
            if existing_app and existing_app.get("user_id") == user["id"]:
                apps_store.update(application_id, {
                    "cover_letter": cover_letter,
                    "updated_at": datetime.utcnow().isoformat(),
                })

        return JSONResponse({"success": True, "cover_letter": cover_letter})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "message": "Cover letter generation failed. Please try again."}, status_code=500)
