import os
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
JOBS_FILE = DATA_DIR / "jobs.json"


def _load_seed_jobs():
    """Load seed jobs if jobs.json is empty."""
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            jobs = json.load(f)
        if jobs:
            return

        seed_file = Path(__file__).parent.parent / "seed" / "jobs_seed.json"
        if seed_file.exists():
            with open(seed_file, "r", encoding="utf-8") as f:
                seed_jobs = json.load(f)
            with open(JOBS_FILE, "w", encoding="utf-8") as f:
                json.dump(seed_jobs, f, indent=2)
            logger.info(f"Loaded {len(seed_jobs)} seed jobs into jobs.json")
        else:
            logger.warning("No seed jobs file found at seed/jobs_seed.json")
    except Exception as e:
        logger.error(f"Error loading seed jobs: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_seed_jobs()
    Path("static/uploads").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI Job Hunter",
    description="AI-powered job discovery and application assistant",
    version="1.0.0",
    lifespan=lifespan,
)

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Register templates globally so routes can import it
app.state.templates = templates

from app.routes import pages, auth, jobs, profile, applications  # noqa: E402

app.include_router(pages.router)
app.include_router(auth.router, prefix="/api/auth")
app.include_router(jobs.router, prefix="/api/jobs")
app.include_router(profile.router, prefix="/api")
app.include_router(applications.router, prefix="/api/applications")

# Cover-letter endpoint lives under /api prefix
from fastapi import Request  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402

@app.get("/logout")
async def logout_redirect(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
