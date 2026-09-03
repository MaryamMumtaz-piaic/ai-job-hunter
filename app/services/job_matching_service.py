import logging
import datetime

logger = logging.getLogger(__name__)


def run_matching(user_id: str, preferences: dict) -> list:
    from app.utils.json_store import JSONStore
    from app.services.openai_service import match_jobs as ai_match_jobs

    resume_store = JSONStore("app/data/resumes.json")
    jobs_store = JSONStore("app/data/jobs.json")
    prefs_store = JSONStore("app/data/preferences.json")

    resume = resume_store.find_one({"user_id": user_id})
    if not resume:
        logger.warning(f"No resume found for user {user_id}, using empty profile")
        resume = {
            "skills": [], "technologies": [], "experience": [],
            "job_titles": [], "summary": "", "years_of_experience": 0,
            "industries": []
        }

    all_jobs = jobs_store.all()
    if not all_jobs:
        logger.warning("No jobs found in jobs.json")
        return []

    try:
        matched = ai_match_jobs(resume, preferences, all_jobs)
    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        matched = []

    existing_pref = prefs_store.find_one({"user_id": user_id})
    now = datetime.datetime.utcnow().isoformat()

    pref_record = dict(preferences)
    pref_record["user_id"] = user_id
    pref_record["last_matched_at"] = now
    pref_record["matched_job_ids"] = [j["id"] for j in matched]

    if existing_pref:
        prefs_store.update({"user_id": user_id}, pref_record)
    else:
        import uuid
        pref_record["id"] = str(uuid.uuid4())
        prefs_store.append(pref_record)

    return matched
