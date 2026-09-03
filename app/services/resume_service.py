import uuid
import datetime
import logging

logger = logging.getLogger(__name__)


def extract_resume_text(file_path: str) -> str:
    from app.utils.file_parser import parse_file
    try:
        return parse_file(file_path)
    except Exception as e:
        logger.error(f"Failed to parse file {file_path}: {e}")
        return ""


def process_resume(user_id: str, file_path: str, portfolio_path: str = "") -> dict:
    from app.services.openai_service import analyze_resume
    from app.utils.json_store import JSONStore

    store = JSONStore("app/data/resumes.json")

    resume_text = extract_resume_text(file_path) if file_path else ""
    portfolio_text = extract_resume_text(portfolio_path) if portfolio_path else ""

    combined_text = resume_text
    if portfolio_text:
        combined_text += f"\n\n--- Portfolio ---\n{portfolio_text}"

    try:
        extracted = analyze_resume(combined_text) if combined_text else {}
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        extracted = {}

    now = datetime.datetime.utcnow().isoformat()

    existing_list = store.find(lambda r: r.get("user_id") == user_id)
    existing = existing_list[-1] if existing_list else None

    resume_record = {
        "id": existing["id"] if existing else str(uuid.uuid4()),
        "user_id": user_id,
        "file_path": file_path,
        "portfolio_path": portfolio_path or "",
        "raw_text": resume_text[:5000],
        "analyzed_at": now,
        "matched_jobs": existing.get("matched_jobs", []) if existing else [],
        "name": extracted.get("name", ""),
        "email": extracted.get("email", ""),
        "summary": extracted.get("summary", ""),
        "skills": extracted.get("skills", []),
        "experience": extracted.get("experience", []),
        "education": extracted.get("education", []),
        "years_of_experience": extracted.get("years_of_experience", 0),
        "job_titles": extracted.get("job_titles", []),
        "industries": extracted.get("industries", []),
        "technologies": extracted.get("technologies", []),
    }

    if existing:
        store.update(existing["id"], resume_record)
    else:
        store.append(resume_record)

    return resume_record
