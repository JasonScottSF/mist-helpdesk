"""In-memory session store — requests.Session objects live here, matching the working Mist app pattern."""

import time
import uuid
import requests
from typing import Optional

_SESSION_TTL = 28800  # 8 hours

_sessions: dict = {}


def _prune():
    now = time.time()
    dead = [k for k, v in list(_sessions.items()) if now - v.get("created_at", now) > _SESSION_TTL]
    for k in dead:
        _sessions.pop(k, None)


def create_session(
    rs: requests.Session,
    cloud_host: str,
    email: str,
    user_name: str,
    authenticated: bool,
    password: str = "",
    orgs: list = None,
) -> str:
    _prune()
    sid = str(uuid.uuid4())
    _sessions[sid] = {
        "requests_session": rs,
        "cloud_host":       cloud_host,
        "email":            email,
        "password":         password,   # kept only for MFA re-login; cleared on success
        "user_name":        user_name,
        "authenticated":    authenticated,
        "org_id":           None,
        "orgs":             orgs or [],
        "created_at":       time.time(),
    }
    return sid


def get_session(sid: Optional[str]) -> Optional[dict]:
    if not sid:
        return None
    _prune()
    return _sessions.get(sid)


def delete_session(sid: str) -> None:
    _sessions.pop(sid, None)


def update_session_org(sid: str, org_id: str) -> None:
    if sid in _sessions:
        _sessions[sid]["org_id"] = org_id
