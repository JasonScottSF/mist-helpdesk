"""Mist API helpers — always use requests.Session() so the cookie jar is maintained correctly."""

import asyncio
import requests
from typing import Optional

MIST_CLOUDS = {
    "api.mist.com":     "Global 01 (US West)",
    "api.gc1.mist.com": "Global 02 (US West)",
    "api.ac2.mist.com": "Global 03 (US East)",
    "api.gc2.mist.com": "Global 04 (Canada)",
    "api.gc4.mist.com": "Global 05 (Americas)",
    "api.eu.mist.com":  "EMEA 01 (Frankfurt)",
    "api.gc3.mist.com": "EMEA 02 (UK)",
    "api.ac6.mist.com": "EMEA 03 (UAE)",
    "api.gc6.mist.com": "EMEA 04 (Saudi Arabia)",
    "api.ac5.mist.com": "APAC 01 (Sydney)",
    "api.gc5.mist.com": "APAC 02 (India)",
    "api.gc7.mist.com": "APAC 03 (Japan)",
}
DEFAULT_CLOUD = "api.mist.com"


def mist_url(cloud_host: str, path: str) -> str:
    return f"https://{cloud_host}/api/v1{path}"


async def _run(fn, *args, **kwargs):
    return await asyncio.to_thread(fn, *args, **kwargs)


# ── Sync helpers (run inside thread pool) ────────────────────────────────────

def _get_csrf(rs: requests.Session) -> Optional[str]:
    return next((v for k, v in rs.cookies.items() if k.startswith("csrftoken")), None)


def _sync_login(rs: requests.Session, cloud_host: str, email: str,
                password: str, two_factor: Optional[str] = None):
    body = {"email": email, "password": password}
    if two_factor:
        body["two_factor"] = two_factor
    return rs.post(mist_url(cloud_host, "/login"), json=body, timeout=15)


def _sync_get_self(rs: requests.Session, cloud_host: str) -> dict:
    sd = rs.get(mist_url(cloud_host, "/self"), timeout=15)
    return sd.json() if sd.ok else {}


def _sync_get(rs: requests.Session, cloud_host: str, path: str) -> dict:
    r = rs.get(mist_url(cloud_host, path), timeout=30)
    r.raise_for_status()
    return r.json()


def _sync_post(rs: requests.Session, cloud_host: str, path: str, body: dict) -> dict:
    csrf = _get_csrf(rs)
    headers = {"X-CSRFToken": csrf} if csrf else {}
    r = rs.post(mist_url(cloud_host, path), json=body, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()


def _sync_logout(rs: requests.Session, cloud_host: str):
    try:
        rs.post(mist_url(cloud_host, "/logout"), timeout=5)
    except Exception:
        pass


# ── Async wrappers ────────────────────────────────────────────────────────────

async def do_login(rs, cloud_host, email, password, two_factor=None):
    return await _run(_sync_login, rs, cloud_host, email, password, two_factor)


async def get_self(rs, cloud_host):
    return await _run(_sync_get_self, rs, cloud_host)


async def api_get(rs, cloud_host, path):
    return await _run(_sync_get, rs, cloud_host, path)


async def api_post(rs, cloud_host, path, body):
    return await _run(_sync_post, rs, cloud_host, path, body)


async def do_logout(rs, cloud_host):
    await _run(_sync_logout, rs, cloud_host)


# ── Domain helpers ────────────────────────────────────────────────────────────

def parse_orgs(self_data: dict) -> list:
    seen = {}
    for p in self_data.get("privileges", []):
        if p.get("scope") == "org" and p.get("org_id"):
            oid = p["org_id"]
            if oid not in seen:
                seen[oid] = {"id": oid, "name": p.get("name", oid)}
    return list(seen.values())


async def get_sites(rs, cloud_host, org_id):
    data = await api_get(rs, cloud_host, f"/orgs/{org_id}/sites")
    sites = data if isinstance(data, list) else data.get("results", [])
    return [{"id": s["id"], "name": s["name"]} for s in sites]


async def get_wireless_clients(rs, cloud_host, site_id):
    data = await api_get(rs, cloud_host, f"/sites/{site_id}/stats/clients")
    return data if isinstance(data, list) else data.get("results", [])


async def get_wired_clients(rs, cloud_host, site_id):
    data = await api_get(rs, cloud_host, f"/sites/{site_id}/stats/wired_clients")
    return data if isinstance(data, list) else data.get("results", [])


def _sync_troubleshoot(rs: requests.Session, cloud_host: str, org_id: str, params: dict) -> dict:
    r = rs.get(mist_url(cloud_host, f"/orgs/{org_id}/troubleshoot"), params=params, timeout=30)
    r.raise_for_status()
    ct = r.headers.get("content-type", "")
    if "json" in ct:
        return r.json()
    return {"text": r.text}


async def marvis_troubleshoot(rs, cloud_host, org_id, params: dict):
    return await _run(_sync_troubleshoot, rs, cloud_host, org_id, params)
