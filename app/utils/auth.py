from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

try:
    import bcrypt as _bcrypt
    def hash_password(password: str) -> str:
        return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    def verify_password(plain: str, hashed: str) -> bool:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
except ImportError:
    import hashlib, os
    def hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        h = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"sha256:{salt}:{h}"
    def verify_password(plain: str, hashed: str) -> bool:
        parts = hashed.split(":", 2)
        if len(parts) != 3 or parts[0] != "sha256":
            return False
        _, salt, h = parts
        return hashlib.sha256((salt + plain).encode()).hexdigest() == h


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
