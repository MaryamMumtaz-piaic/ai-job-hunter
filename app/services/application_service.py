import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

VALID_STATUSES = ["Draft", "Pending Approval", "Approved", "Submitted", "Interview", "Rejected", "Offer"]


def create_application(user_id: str, job_id: str, job_data: dict, candidate_info: dict) -> dict:
    from app.utils.json_store import JSONStore
    store = JSONStore("app/data/applications.json")

    existing = store.find_one({"user_id": user_id, "job_id": job_id})
    if existing:
        return existing

    now = datetime.datetime.utcnow().isoformat()
    app_record = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "job_id": job_id,
        "status": "Draft",
        "created_at": now,
        "updated_at": now,
        "job_title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "job_location": job_data.get("location", ""),
        "job_work_mode": job_data.get("work_mode", ""),
        "job_salary_min": job_data.get("salary_min"),
        "job_salary_max": job_data.get("salary_max"),
        "job_currency": job_data.get("currency", "USD"),
        "job_description": job_data.get("description", ""),
        "match_score": job_data.get("match_score"),
        "candidate_name": candidate_info.get("name", ""),
        "candidate_email": candidate_info.get("email", ""),
        "candidate_phone": candidate_info.get("phone", ""),
        "candidate_location": candidate_info.get("location", ""),
        "candidate_linkedin": candidate_info.get("linkedin", ""),
        "candidate_github": candidate_info.get("github", ""),
        "candidate_skills": candidate_info.get("skills", []),
        "candidate_experience": candidate_info.get("experience", []),
        "resume_path": candidate_info.get("resume_path", ""),
        "portfolio_path": candidate_info.get("portfolio_path", ""),
        "cover_letter": "",
        "notes": "",
    }

    store.append(app_record)
    return app_record


def update_application(application_id: str, user_id: str, updates: dict) -> dict:
    from app.utils.json_store import JSONStore
    store = JSONStore("app/data/applications.json")

    app = store.find_one({"id": application_id})
    if not app:
        raise ValueError(f"Application {application_id} not found")
    if app["user_id"] != user_id:
        raise PermissionError("Access denied")

    updates["updated_at"] = datetime.datetime.utcnow().isoformat()
    store.update({"id": application_id}, updates)

    return store.find_one({"id": application_id})


def update_application_status(application_id: str, user_id: str, status: str) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
    return update_application(application_id, user_id, {"status": status})


def save_cover_letter(application_id: str, user_id: str, cover_letter: str) -> dict:
    return update_application(application_id, user_id, {"cover_letter": cover_letter})


def get_user_applications(user_id: str) -> list:
    from app.utils.json_store import JSONStore
    store = JSONStore("app/data/applications.json")
    apps = store.find({"user_id": user_id})
    apps.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return apps


def get_application(application_id: str, user_id: str) -> dict:
    from app.utils.json_store import JSONStore
    store = JSONStore("app/data/applications.json")
    app = store.find_one({"id": application_id})
    if not app:
        raise ValueError(f"Application {application_id} not found")
    if app["user_id"] != user_id:
        raise PermissionError("Access denied")
    return app


def get_user_stats(user_id: str) -> dict:
    from app.utils.json_store import JSONStore
    store = JSONStore("app/data/applications.json")
    apps = store.find({"user_id": user_id})

    stats = {
        "total": len(apps),
        "draft": 0,
        "pending": 0,
        "approved": 0,
        "submitted": 0,
        "interview": 0,
        "rejected": 0,
        "offer": 0,
    }

    for app in apps:
        status = app.get("status", "Draft")
        if status == "Draft":
            stats["draft"] += 1
        elif status == "Pending Approval":
            stats["pending"] += 1
        elif status == "Approved":
            stats["approved"] += 1
        elif status == "Submitted":
            stats["submitted"] += 1
        elif status == "Interview":
            stats["interview"] += 1
        elif status == "Rejected":
            stats["rejected"] += 1
        elif status == "Offer":
            stats["offer"] += 1

    return stats
