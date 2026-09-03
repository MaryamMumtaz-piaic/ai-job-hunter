from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.json_store import JSONStore
import uuid
import re
from datetime import datetime

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(pw: str) -> str:
        return pwd_context.hash(pw)
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
except ImportError:
    import hashlib, os
    def hash_password(pw: str) -> str:
        salt = os.urandom(16).hex()
        h = hashlib.sha256((salt + pw).encode()).hexdigest()
        return f"{salt}:{h}"
    def verify_password(plain: str, hashed: str) -> bool:
        parts = hashed.split(":", 1)
        if len(parts) != 2:
            return False
        salt, h = parts
        return hashlib.sha256((salt + plain).encode()).hexdigest() == h

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/signup")
async def api_signup(request: Request):
    try:
        body = await request.json()
        full_name = body.get("full_name", "").strip()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")
        confirm_password = body.get("confirm_password", "")

        errors = _validate_signup(full_name, email, password, confirm_password)
        if errors:
            return JSONResponse({"success": False, "errors": errors}, status_code=400)

        users = JSONStore("app/data/users.json")
        existing = users.find(lambda u: u.get("email") == email)
        if existing:
            return JSONResponse({"success": False, "errors": {"email": "Email already registered"}}, status_code=400)

        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "password_hash": hash_password(password),
            "avatar_initials": _get_initials(full_name),
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "saved_jobs": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        users.append(new_user)
        return JSONResponse({"success": True, "redirect": "/signin"})
    except Exception as e:
        return JSONResponse({"success": False, "errors": {"general": "Registration failed. Please try again."}}, status_code=500)


@router.post("/signin")
async def api_signin(request: Request):
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        if not email or not password:
            return JSONResponse({"success": False, "errors": {"general": "Email and password are required"}}, status_code=400)

        users = JSONStore("app/data/users.json")
        matched = users.find(lambda u: u.get("email") == email)
        if not matched:
            return JSONResponse({"success": False, "errors": {"general": "Invalid email or password"}}, status_code=401)

        user = matched[0]
        if not verify_password(password, user.get("password_hash", "")):
            return JSONResponse({"success": False, "errors": {"general": "Invalid email or password"}}, status_code=401)

        request.session["user_id"] = user["id"]
        return JSONResponse({"success": True, "redirect": "/dashboard", "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "avatar_initials": user.get("avatar_initials", _get_initials(user["full_name"])),
        }})
    except Exception as e:
        return JSONResponse({"success": False, "errors": {"general": "Login failed. Please try again."}}, status_code=500)


@router.post("/logout")
async def api_logout(request: Request):
    request.session.clear()
    return JSONResponse({"success": True, "redirect": "/"})


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


def _validate_signup(full_name, email, password, confirm_password):
    errors = {}
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters"
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors["email"] = "Valid email address is required"
    if not password or len(password) < 6:
        errors["password"] = "Password must be at least 6 characters"
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"
    return errors


def _get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"
