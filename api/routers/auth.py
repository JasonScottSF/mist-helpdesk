from fastapi import APIRouter, Response, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
import mist_client
from session_store import (
    _dump_cookies,
    build_requests_session,
    create_session,
    delete_session,
    get_session,
    store_pending_mfa,
    pop_pending_mfa,
    update_session_org,
)

router = APIRouter()

SESSION_COOKIE = "hd_session"
COOKIE_OPTS = dict(httponly=True, samesite="lax", path="/")


class LoginRequest(BaseModel):
    email: str
    password: str


class MfaRequest(BaseModel):
    code: str
    token: str       # the pending-MFA token returned by /login


class OrgSelectRequest(BaseModel):
    org_id: str


@router.post("/login")
async def login(req: LoginRequest, response: Response):
    try:
        data, session, mfa_required = await mist_client.login(req.email, req.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    cookies = _dump_cookies(session)

    if mfa_required:
        mfa_token = store_pending_mfa(req.email, req.password, cookies)
        return {"mfa_required": True, "mfa_token": mfa_token}

    # Full login — build org list and create session
    try:
        self_data = await mist_client.get_self(session)
    except Exception:
        raise HTTPException(status_code=502, detail="Could not fetch user profile from Mist")

    orgs = mist_client.parse_orgs(self_data)
    if not orgs:
        raise HTTPException(status_code=403, detail="No organisation access found for this account")

    org_id = orgs[0]["id"] if len(orgs) == 1 else None
    sid = create_session(cookies, self_data, orgs, org_id)

    response.set_cookie(SESSION_COOKIE, sid, max_age=28800, **COOKIE_OPTS)
    return {
        "mfa_required": False,
        "orgs": orgs,
        "org_id": org_id,
        "user": {"email": self_data.get("email"), "name": self_data.get("name")},
    }


@router.post("/mfa")
async def mfa(req: MfaRequest, response: Response):
    pending = pop_pending_mfa(req.token)
    if not pending:
        raise HTTPException(status_code=400, detail="MFA session expired — please log in again")

    try:
        data, session, _ = await mist_client.login(
            pending["email"], pending["password"], two_factor=req.code
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid MFA code")

    try:
        self_data = await mist_client.get_self(session)
    except Exception:
        raise HTTPException(status_code=502, detail="Could not fetch user profile from Mist")

    orgs = mist_client.parse_orgs(self_data)
    if not orgs:
        raise HTTPException(status_code=403, detail="No organisation access found")

    cookies = _dump_cookies(session)
    org_id = orgs[0]["id"] if len(orgs) == 1 else None
    sid = create_session(cookies, self_data, orgs, org_id)

    response.set_cookie(SESSION_COOKIE, sid, max_age=28800, **COOKIE_OPTS)
    return {
        "orgs": orgs,
        "org_id": org_id,
        "user": {"email": self_data.get("email"), "name": self_data.get("name")},
    }


@router.post("/org")
async def select_org(req: OrgSelectRequest, response: Response, hd_session: Optional[str] = Cookie(None)):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess:
        raise HTTPException(status_code=401, detail="Session expired")

    valid_ids = [o["id"] for o in sess.get("orgs", [])]
    if req.org_id not in valid_ids:
        raise HTTPException(status_code=403, detail="Not authorised for that org")

    update_session_org(hd_session, req.org_id)
    return {"org_id": req.org_id}


@router.get("/me")
async def me(hd_session: Optional[str] = Cookie(None)):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess:
        raise HTTPException(status_code=401, detail="Session expired")
    return {
        "user": sess.get("user"),
        "orgs": sess.get("orgs"),
        "org_id": sess.get("org_id"),
    }


@router.post("/logout")
async def logout(response: Response, hd_session: Optional[str] = Cookie(None)):
    if hd_session:
        delete_session(hd_session)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}
