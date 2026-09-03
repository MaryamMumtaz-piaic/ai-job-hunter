from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.utils.json_store import JSONStore
from app.utils.auth import get_current_user
import os
import uuid
import shutil
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "static/uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/api/profile")
async def get_profile(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    resumes_store = JSONStore("app/data/resumes.json")
    resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
    latest_resume = resume_data[-1] if resume_data else None

    return JSONResponse({
        "success": True,
        "user": {k: v for k, v in user.items() if k != "password_hash"},
        "resume": latest_resume,
    })


@router.put("/api/profile")
async def update_profile(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        users_store = JSONStore("app/data/users.json")
        allowed_fields = ["full_name", "phone", "location", "linkedin", "github", "bio"]
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if "full_name" in updates and updates["full_name"]:
            name = updates["full_name"]
            parts = name.strip().split()
            if len(parts) >= 2:
                updates["avatar_initials"] = (parts[0][0] + parts[-1][0]).upper()
            else:
                updates["avatar_initials"] = name[:2].upper()

        users_store.update(user["id"], updates)

        # Also update resume profile fields if provided
        resume_fields = ["summary", "skills", "experience", "education", "technologies", "industries"]
        resume_updates = {k: v for k, v in body.items() if k in resume_fields}
        if resume_updates:
            resumes_store = JSONStore("app/data/resumes.json")
            resume_data = resumes_store.find(lambda r: r.get("user_id") == user["id"])
            if resume_data:
                latest = resume_data[-1]
                resumes_store.update(latest["id"], resume_updates)

        return JSONResponse({"success": True, "message": "Profile updated successfully"})
    except Exception as e:
        return JSONResponse({"success": False, "message": "Failed to update profile"}, status_code=500)


@router.post("/api/resume/upload")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return JSONResponse({"success": False, "message": f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"}, status_code=400)

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            return JSONResponse({"success": False, "message": "File too large. Maximum size is 10MB"}, status_code=400)

        safe_name = f"{user['id']}_{uuid.uuid4().hex[:8]}{ext}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        with open(file_path, "wb") as f:
            f.write(content)

        # Store file reference in user record
        users_store = JSONStore("app/data/users.json")
        field = "resume_file" if "portfolio" not in (file.filename or "").lower() else "portfolio_file"
        users_store.update(user["id"], {
            field: safe_name,
            f"{field}_original": file.filename,
            f"{field}_uploaded_at": datetime.utcnow().isoformat(),
        })

        return JSONResponse({
            "success": True,
            "file_name": safe_name,
            "original_name": file.filename,
            "file_type": ext.lstrip(".").upper(),
            "field": field,
        })
    except Exception as e:
        return JSONResponse({"success": False, "message": "Upload failed. Please try again."}, status_code=500)


@router.post("/api/resume/analyze")
async def analyze_resume(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        file_name = body.get("file_name") or user.get("resume_file")

        if not file_name:
            return JSONResponse({"success": False, "message": "No resume file found. Please upload a resume first."}, status_code=400)

        file_path = os.path.join(UPLOAD_DIR, file_name)
        if not os.path.exists(file_path):
            return JSONResponse({"success": False, "message": "Resume file not found on server."}, status_code=404)

        from app.services.resume_service import extract_resume_text
        from app.services.openai_service import analyze_resume as ai_analyze

        text = extract_resume_text(file_path)
        profile = await ai_analyze(text)

        resumes_store = JSONStore("app/data/resumes.json")
        resume_id = str(uuid.uuid4())
        resume_record = {
            "id": resume_id,
            "user_id": user["id"],
            "file_name": file_name,
            "raw_text": text[:5000],
            "analyzed_at": datetime.utcnow().isoformat(),
            "matched_jobs": [],
            **profile,
        }
        resumes_store.append(resume_record)

        return JSONResponse({"success": True, "profile": profile, "resume_id": resume_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "message": "Resume analysis failed. Please try again."}, status_code=500)


@router.get("/api/preferences")
async def get_preferences(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    prefs_store = JSONStore("app/data/preferences.json")
    prefs = prefs_store.find(lambda p: p.get("user_id") == user["id"])
    latest = prefs[-1] if prefs else None

    return JSONResponse({"success": True, "preferences": latest})


@router.put("/api/preferences")
async def save_preferences(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        prefs_store = JSONStore("app/data/preferences.json")
        existing = prefs_store.find(lambda p: p.get("user_id") == user["id"])

        pref_data = {
            "user_id": user["id"],
            "job_type": body.get("job_type", "Full-time"),
            "work_mode": body.get("work_mode", "Any"),
            "desired_titles": body.get("desired_titles", []),
            "country": body.get("country", "Any"),
            "city": body.get("city", ""),
            "salary_min": body.get("salary_min"),
            "salary_max": body.get("salary_max"),
            "experience_level": body.get("experience_level", "Any"),
            "employment_preference": body.get("employment_preference", "Any"),
            "skills": body.get("skills", []),
            "updated_at": datetime.utcnow().isoformat(),
        }

        if existing:
            prefs_store.update(existing[-1]["id"], pref_data)
        else:
            pref_data["id"] = str(uuid.uuid4())
            pref_data["created_at"] = datetime.utcnow().isoformat()
            prefs_store.append(pref_data)

        return JSONResponse({"success": True, "message": "Preferences saved"})
    except Exception as e:
        return JSONResponse({"success": False, "message": "Failed to save preferences"}, status_code=500)
