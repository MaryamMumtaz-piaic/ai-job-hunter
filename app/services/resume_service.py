import uuid
import datetime
import logging

logger = logging.getLogger(__name__)


def process_resume(user_id: str, file_path: str, portfolio_path: str = "") -> dict:
    from app.utils.file_parser import parse_file
    from app.services.openai_service import analyze_resume
    from app.utils.json_store import JSONStore

    store = JSONStore("app/data/resumes.json")

    try:
        resume_text = parse_file(file_path) if file_path else ""
    except Exception as e:
        logger.error(f"Failed to parse resume file: {e}")
        resume_text = ""

    portfolio_text = ""
    if portfolio_path:
        try:
            portfolio_text = parse_file(portfolio_path)
        except Exception as e:
            logger.error(f"Failed to parse portfolio file: {e}")

    combined_text = resume_text
    if portfolio_text:
        combined_text += f"\n\n--- Portfolio ---\n{portfolio_text}"

    try:
        extracted = analyze_resume(combined_text) if combined_text else {}
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        extracted = {}

    now = datetime.datetime.utcnow().isoformat()

    existing = store.find_one({"user_id": user_id})

    resume_record = {
        "id": existing["id"] if existing else str(uuid.uuid4()),
        "user_id": user_id,
        "file_path": file_path,
        "portfolio_path": portfolio_path or "",
        "resume_text": resume_text[:5000],
        "analyzed_at": now,
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
        store.update({"user_id": user_id}, resume_record)
    else:
        store.append(resume_record)

    return resume_record
