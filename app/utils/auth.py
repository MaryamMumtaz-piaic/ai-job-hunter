from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_current_user(request: Request) -> dict | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    from app.utils.json_store import JSONStore
    users = JSONStore("app/data/users.json")
    return users.find_by_id(user_id)


def require_auth(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_auth_redirect(request: Request):
    """For page routes — redirects to /signin instead of raising 401."""
    user = get_current_user(request)
    if not user:
        return None
    return user
