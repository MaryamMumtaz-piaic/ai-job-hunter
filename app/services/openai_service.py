import os
import json
import logging

logger = logging.getLogger(__name__)

MOCK_MODE = os.getenv("OPENAI_MOCK_MODE", "true").lower() == "true"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_client():
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAI(api_key=api_key)
    except ImportError:
        raise RuntimeError("openai package not installed")


def analyze_resume(resume_text: str) -> dict:
    if MOCK_MODE:
        return {
            "name": "Demo User",
            "email": "demo@example.com",
            "summary": "Experienced Python and AI developer with 3 years of experience building web applications and AI systems.",
            "skills": ["Python", "FastAPI", "React", "OpenAI", "SQL", "Docker", "Git"],
            "experience": [
                {
                    "title": "Backend Developer",
                    "company": "Tech Corp",
                    "duration": "2022-2024",
                    "description": "Built REST APIs with FastAPI and PostgreSQL. Integrated OpenAI APIs for intelligent features."
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "institution": "University of Technology",
                    "year": "2022"
                }
            ],
            "years_of_experience": 3,
            "job_titles": ["Backend Developer", "Python Developer", "AI Engineer"],
            "industries": ["Technology", "Software Development"],
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis", "OpenAI API", "Docker"]
        }

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume analyzer. Extract structured information "
                        "accurately from the resume text provided. Do not invent information. "
                        "If something is missing, return an empty value. Return valid JSON only, "
                        "no markdown, no explanation."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Extract the following fields from this resume and return as JSON:\n"
                        f"name, email, summary, skills (array), experience (array of objects with "
                        f"title/company/duration/description), education (array of objects with "
                        f"degree/institution/year), years_of_experience (integer), job_titles (array), "
                        f"industries (array), technologies (array).\n\n"
                        f"Resume:\n{resume_text[:4000]}"
                    )
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        return {
            "name": "", "email": "", "summary": "",
            "skills": [], "experience": [], "education": [],
            "years_of_experience": 0, "job_titles": [],
            "industries": [], "technologies": []
        }


def _local_prefilter(candidate_profile: dict, preferences: dict, jobs: list) -> list:
    work_mode = preferences.get("work_mode", "Any")
    employment_type = preferences.get("employment_type", "")
    experience_level = preferences.get("experience_level", "Any")
    salary_min = preferences.get("salary_min") or 0
    salary_max = preferences.get("salary_max") or float("inf")

    candidate_skills = set(s.lower() for s in candidate_profile.get("skills", []) + candidate_profile.get("technologies", []))
    desired_titles = [t.lower() for t in preferences.get("desired_titles", [])]

    scored = []
    for job in jobs:
        # Work mode filter
        if work_mode != "Any" and job.get("work_mode", "").lower() != work_mode.lower():
            continue

        # Employment type filter
        if employment_type and employment_type != "Any":
            if job.get("employment_type", "").lower() != employment_type.lower():
                continue

        # Experience level filter
        if experience_level != "Any":
            if job.get("experience_level", "").lower() != experience_level.lower():
                continue

        # Salary filter
        job_min = job.get("salary_min") or 0
        job_max = job.get("salary_max") or float("inf")
        if salary_max and job_min and job_min > salary_max:
            continue
        if salary_min and job_max and job_max < salary_min:
            continue

        # Keyword overlap score
        job_skills = set(s.lower() for s in job.get("skills", []) + job.get("requirements", []))
        overlap = len(candidate_skills & job_skills)

        # Title match bonus
        title_bonus = 0
        job_title_lower = job.get("title", "").lower()
        for dt in desired_titles:
            if dt in job_title_lower or job_title_lower in dt:
                title_bonus = 20
                break

        raw_score = overlap * 5 + title_bonus
        scored.append((raw_score, job))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [j for _, j in scored[:50]]


def _mock_match_jobs(candidate_profile: dict, preferences: dict, jobs: list) -> list:
    filtered = _local_prefilter(candidate_profile, preferences, jobs)
    candidate_skills = [s.lower() for s in candidate_profile.get("skills", []) + candidate_profile.get("technologies", [])]
    candidate_titles = [t.lower() for t in candidate_profile.get("job_titles", [])]

    high_keywords = ["ai", "python", "backend", "fastapi", "machine learning", "ml", "llm", "agent", "openai", "data"]
    medium_keywords = ["frontend", "full stack", "fullstack", "react", "node", "javascript", "typescript", "devops", "cloud"]

    results = []
    for job in filtered:
        job_title = job.get("title", "").lower()
        job_skills = [s.lower() for s in job.get("skills", [])]
        all_job_text = job_title + " " + " ".join(job_skills)

        high_match = any(k in all_job_text for k in high_keywords)
        medium_match = any(k in all_job_text for k in medium_keywords)

        matched_skills = [s for s in candidate_skills if s in all_job_text]
        missing_skills = [s for s in job_skills if s not in candidate_skills][:5]

        if high_match:
            score = 85 + min(len(matched_skills) * 2, 10)
            reason = (
                f"Strong match: your Python and AI skills align well with this {job.get('title')} role. "
                f"Matched {len(matched_skills)} of your key skills."
            )
        elif medium_match:
            score = 65 + min(len(matched_skills) * 3, 15)
            reason = (
                f"Good match: your technical background transfers to this {job.get('title')} position. "
                f"Some skill overlap identified."
            )
        else:
            score = 45 + min(len(matched_skills) * 4, 20)
            reason = (
                f"Partial match: limited overlap between your profile and this {job.get('title')} role, "
                f"but transferable skills exist."
            )

        score = min(score, 98)
        job_copy = dict(job)
        job_copy["match_score"] = score
        job_copy["match_reason"] = reason
        job_copy["matched_skills"] = matched_skills[:8]
        job_copy["missing_skills"] = missing_skills
        results.append(job_copy)

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:30]


def match_jobs(candidate_profile: dict, preferences: dict, jobs: list) -> list:
    if MOCK_MODE:
        return _mock_match_jobs(candidate_profile, preferences, jobs)

    filtered = _local_prefilter(candidate_profile, preferences, jobs)
    if not filtered:
        return []

    candidate_skills = candidate_profile.get("skills", []) + candidate_profile.get("technologies", [])

    job_summaries = []
    for j in filtered:
        job_summaries.append({
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company"),
            "skills": j.get("skills", [])[:10],
            "requirements": j.get("requirements", [])[:5],
            "description_snippet": (j.get("description", ""))[:200]
        })

    prompt = (
        f"Candidate profile:\n"
        f"- Skills: {', '.join(candidate_skills[:20])}\n"
        f"- Experience: {candidate_profile.get('years_of_experience', 0)} years\n"
        f"- Titles: {', '.join(candidate_profile.get('job_titles', []))}\n"
        f"- Summary: {candidate_profile.get('summary', '')[:300]}\n\n"
        f"Preferences:\n"
        f"- Desired titles: {', '.join(preferences.get('desired_titles', []))}\n"
        f"- Work mode: {preferences.get('work_mode', 'Any')}\n"
        f"- Experience level: {preferences.get('experience_level', 'Any')}\n\n"
        f"Jobs (JSON array):\n{json.dumps(job_summaries, indent=2)[:8000]}\n\n"
        f"Rank these jobs by fit for this candidate. Return a JSON array of objects with: "
        f"id, match_score (0-100 integer), match_reason (1-2 sentences), "
        f"matched_skills (array), missing_skills (array). Return top 20 only."
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional job matching AI. Rank jobs accurately based on candidate fit. Return valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        raw = json.loads(response.choices[0].message.content)
        ranked = raw if isinstance(raw, list) else raw.get("jobs", raw.get("results", []))

        job_map = {j["id"]: j for j in filtered}
        results = []
        for item in ranked:
            job_id = item.get("id")
            if job_id in job_map:
                enriched = dict(job_map[job_id])
                enriched["match_score"] = item.get("match_score", 50)
                enriched["match_reason"] = item.get("match_reason", "")
                enriched["matched_skills"] = item.get("matched_skills", [])
                enriched["missing_skills"] = item.get("missing_skills", [])
                results.append(enriched)

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    except Exception as e:
        logger.error(f"AI job matching failed, falling back to mock: {e}")
        return _mock_match_jobs(candidate_profile, preferences, filtered)


def generate_cover_letter(candidate_profile: dict, job: dict) -> str:
    name = candidate_profile.get("name", "the candidate")
    skills = ", ".join(candidate_profile.get("skills", [])[:8])
    experience_items = candidate_profile.get("experience", [])
    exp_summary = ""
    if experience_items:
        latest = experience_items[0]
        exp_summary = f"{latest.get('title', '')} at {latest.get('company', '')} ({latest.get('duration', '')})"
    summary = candidate_profile.get("summary", "")
    years = candidate_profile.get("years_of_experience", 0)

    job_title = job.get("title", "")
    company = job.get("company", "")
    description = job.get("description", "")[:600]
    job_skills = ", ".join(job.get("skills", [])[:6])

    if MOCK_MODE:
        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong interest in the {job_title} position at {company}. "
            f"With {years} years of hands-on experience in {skills}, I am confident that my background "
            f"aligns well with the requirements of this role.\n\n"
            f"In my most recent role as {exp_summary if exp_summary else 'a software engineer'}, I developed "
            f"a solid foundation in building robust, scalable systems. Your team's work resonates with my "
            f"professional goals, and I am particularly drawn to this opportunity because of {company}'s "
            f"commitment to innovation in its field.\n\n"
            f"I bring expertise in {skills}, which directly maps to the key requirements you are looking for — "
            f"including {job_skills}. I thrive in collaborative environments and consistently deliver "
            f"high-quality results under deadline.\n\n"
            f"I would welcome the opportunity to discuss how my experience can contribute to {company}'s "
            f"continued success. Thank you for your time and consideration.\n\n"
            f"Sincerely,\n{name}"
        )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert career coach writing personalized cover letters. "
                        "Write professionally, naturally, and persuasively. Maximum 4 paragraphs. "
                        "Do not use generic filler phrases. Be specific and compelling."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write a cover letter for this candidate applying to this job.\n\n"
                        f"Candidate:\n"
                        f"- Name: {name}\n"
                        f"- Summary: {summary[:300]}\n"
                        f"- Key skills: {skills}\n"
                        f"- Recent experience: {exp_summary}\n"
                        f"- Years of experience: {years}\n\n"
                        f"Job:\n"
                        f"- Title: {job_title}\n"
                        f"- Company: {company}\n"
                        f"- Required skills: {job_skills}\n"
                        f"- Description: {description}\n\n"
                        f"Write a complete, professional cover letter addressed to the hiring team."
                    )
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my interest in the {job_title} position. "
            f"With {years} years of experience in {skills}, I believe I would be a strong fit.\n\n"
            f"I look forward to the opportunity to contribute to {company}.\n\n"
            f"Sincerely,\n{name}"
        )
