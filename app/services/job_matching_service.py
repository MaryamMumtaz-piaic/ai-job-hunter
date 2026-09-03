import logging
import uuid
import datetime

logger = logging.getLogger(__name__)


def run_matching(user_id: str, preferences: dict) -> list:
    from app.utils.json_store import JSONStore
    from app.services.openai_service import match_jobs as ai_match_jobs

    resume_store = JSONStore("app/data/resumes.json")
    jobs_store = JSONStore("app/data/jobs.json")
    prefs_store = JSONStore("app/data/preferences.json")

    resumes = resume_store.find(lambda r: r.get("user_id") == user_id)
    resume = resumes[-1] if resumes else {
        "skills": [], "technologies": [], "experience": [],
        "job_titles": [], "summary": "", "years_of_experience": 0,
        "industries": []
    }

    all_jobs = jobs_store.read()
    if not all_jobs:
        logger.warning("No jobs found in jobs.json")
        return []

    try:
        matched = ai_match_jobs(resume, preferences, all_jobs)
    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        matched = []

    existing_prefs = prefs_store.find(lambda p: p.get("user_id") == user_id)
    now = datetime.datetime.utcnow().isoformat()

    pref_record = dict(preferences)
    pref_record["user_id"] = user_id
    pref_record["last_matched_at"] = now
    pref_record["matched_job_ids"] = [j.get("job_id", j.get("id", "")) for j in matched]

    if existing_prefs:
        prefs_store.update(existing_prefs[-1]["id"], pref_record)
    else:
        pref_record["id"] = str(uuid.uuid4())
        pref_record["created_at"] = now
        prefs_store.append(pref_record)

    return matched
