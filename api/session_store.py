"""Redis-backed session store. Sessions hold the serialised Mist cookie jar."""

import json
import uuid
import requests
from typing import Optional
from redis import Redis
from config import settings

_redis: Optional[Redis] = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


# ── Cookie jar helpers ────────────────────────────────────────────────────────

def _dump_cookies(session: requests.Session) -> list:
    """Serialise a requests.Session cookie jar to a list of dicts."""
    return [
        {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
        }
        for c in session.cookies
    ]


def _load_cookies(session: requests.Session, cookies: list) -> None:
    """Restore a serialised cookie list into a requests.Session."""
    for c in cookies:
        session.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])


# ── Session CRUD ──────────────────────────────────────────────────────────────

def create_session(cookies: list, user: dict, orgs: list, org_id: str) -> str:
    sid = str(uuid.uuid4())
    data = {
        "cookies": cookies,
        "user": user,
        "orgs": orgs,
        "org_id": org_id,
    }
    get_redis().setex(f"session:{sid}", settings.session_ttl, json.dumps(data))
    return sid


def get_session(sid: str) -> Optional[dict]:
    raw = get_redis().get(f"session:{sid}")
    return json.loads(raw) if raw else None


def delete_session(sid: str) -> None:
    get_redis().delete(f"session:{sid}")


def update_session_org(sid: str, org_id: str) -> None:
    data = get_session(sid)
    if data:
        data["org_id"] = org_id
        get_redis().setex(f"session:{sid}", settings.session_ttl, json.dumps(data))


# ── Pending MFA ───────────────────────────────────────────────────────────────

def store_pending_mfa(email: str, password: str, cookies: list) -> str:
    """Store credentials briefly while we wait for the MFA code."""
    token = str(uuid.uuid4())
    data = {"email": email, "password": password, "cookies": cookies}
    get_redis().setex(f"mfa:{token}", settings.mfa_ttl, json.dumps(data))
    return token


def pop_pending_mfa(token: str) -> Optional[dict]:
    key = f"mfa:{token}"
    raw = get_redis().get(key)
    if raw:
        get_redis().delete(key)
        return json.loads(raw)
    return None


# ── Build a live requests.Session from stored data ────────────────────────────

def build_requests_session(session_data: dict) -> requests.Session:
    s = requests.Session()
    _load_cookies(s, session_data["cookies"])
    return s


def get_csrf(session: requests.Session) -> Optional[str]:
    """Find the CSRF token — key starts with 'csrftoken' (may have cloud suffix)."""
    return next(
        (v for k, v in session.cookies.items() if k.startswith("csrftoken")),
        None,
    )
