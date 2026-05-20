"""Mist API helpers — always use requests.Session() to keep the cookie jar intact."""

import asyncio
import requests
from typing import Optional
from config import settings
from session_store import get_csrf

BASE = settings.mist_base


# ── run sync requests in thread pool so FastAPI stays async ──────────────────

async def _run(fn, *args, **kwargs):
    return await asyncio.to_thread(fn, *args, **kwargs)


# ── Auth ──────────────────────────────────────────────────────────────────────

def _login_sync(email: str, password: str, two_factor: Optional[str] = None):
    """
    Login to Mist. Returns (response_json, session, two_factor_required).
    MFA is a re-POST to /login with all three fields — NOT a separate endpoint.
    """
    s = requests.Session()
    body = {"email": email, "password": password}
    if two_factor:
        body["two_factor"] = two_factor

    r = s.post(f"{BASE}/api/v1/login", json=body)
    r.raise_for_status()
    data = r.json()
    return data, s, data.get("two_factor_required", False)


async def login(email: str, password: str, two_factor: Optional[str] = None):
    return await _run(_login_sync, email, password, two_factor)


# ── Generic API calls ─────────────────────────────────────────────────────────

def _get_sync(session: requests.Session, path: str) -> dict:
    r = session.get(f"{BASE}{path}")
    r.raise_for_status()
    return r.json()


def _post_sync(session: requests.Session, path: str, body: dict) -> dict:
    csrf = get_csrf(session)
    headers = {"X-CSRFToken": csrf} if csrf else {}
    r = session.post(f"{BASE}{path}", json=body, headers=headers)
    r.raise_for_status()
    return r.json()


async def api_get(session: requests.Session, path: str) -> dict:
    return await _run(_get_sync, session, path)


async def api_post(session: requests.Session, path: str, body: dict) -> dict:
    return await _run(_post_sync, session, path, body)


# ── Domain helpers ────────────────────────────────────────────────────────────

async def get_self(session: requests.Session) -> dict:
    return await api_get(session, "/api/v1/self")


def parse_orgs(self_data: dict) -> list:
    """Extract org list from the /self privileges array."""
    seen = {}
    for p in self_data.get("privileges", []):
        if p.get("scope") == "org" and p.get("org_id"):
            oid = p["org_id"]
            if oid not in seen:
                seen[oid] = {"id": oid, "name": p.get("name", oid)}
    return list(seen.values())


async def get_sites(session: requests.Session, org_id: str) -> list:
    data = await api_get(session, f"/api/v1/orgs/{org_id}/sites")
    return [{"id": s["id"], "name": s["name"]} for s in data]


async def get_wireless_clients(session: requests.Session, site_id: str) -> list:
    data = await api_get(session, f"/api/v1/sites/{site_id}/clients")
    return data if isinstance(data, list) else data.get("results", [])


async def get_wired_clients(session: requests.Session, site_id: str) -> list:
    data = await api_get(session, f"/api/v1/sites/{site_id}/wired_clients")
    return data if isinstance(data, list) else data.get("results", [])


async def marvis_query(session: requests.Session, org_id: str, query: str) -> dict:
    return await api_post(session, f"/api/v1/orgs/{org_id}/marvis/search", {"query": query})
