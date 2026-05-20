import requests as req_lib
from fastapi import APIRouter, Response, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
import mist_client
from mist_client import MIST_CLOUDS, DEFAULT_CLOUD
from session_store import create_session, delete_session, get_session, update_session_org

router = APIRouter()

SESSION_COOKIE = "hd_session"
COOKIE_OPTS = dict(httponly=True, samesite="lax", path="/")


class LoginRequest(BaseModel):
    email: str
    password: str
    cloud: Optional[str] = DEFAULT_CLOUD


class MfaRequest(BaseModel):
    code: str
    mfa_token: str


class OrgSelectRequest(BaseModel):
    org_id: str


@router.get("/clouds")
async def clouds():
    return {"clouds": [{"host": k, "label": v} for k, v in MIST_CLOUDS.items()]}


@router.post("/login")
async def login(req: LoginRequest, response: Response):
    cloud = req.cloud if req.cloud in MIST_CLOUDS else DEFAULT_CLOUD
    rs = req_lib.Session()

    r = await mist_client.do_login(rs, cloud, req.email, req.password)
    if r.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not r.ok:
        raise HTTPException(status_code=502, detail="Mist API error during login")

    self_data = await mist_client.get_self(rs, cloud)
    mfa_required = self_data.get("two_factor_required") and not self_data.get("two_factor_passed")

    if mfa_required:
        sid = create_session(
            rs=rs,
            cloud_host=cloud,
            email=req.email,
            user_name="",
            authenticated=False,
            password=req.password,
        )
        return {"mfa_required": True, "mfa_token": sid}

    orgs = mist_client.parse_orgs(self_data)
    if not orgs:
        raise HTTPException(status_code=403, detail="No organisation access found for this account")

    user_name = self_data.get("name", req.email)
    org_id = orgs[0]["id"] if len(orgs) == 1 else None

    sid = create_session(
        rs=rs,
        cloud_host=cloud,
        email=req.email,
        user_name=user_name,
        authenticated=True,
        orgs=orgs,
    )
    if org_id:
        update_session_org(sid, org_id)

    response.set_cookie(SESSION_COOKIE, sid, max_age=28800, **COOKIE_OPTS)
    return {
        "mfa_required": False,
        "orgs": orgs,
        "org_id": org_id,
        "user": {"email": req.email, "name": user_name},
    }


@router.post("/mfa")
async def mfa(req: MfaRequest, response: Response):
    sess = get_session(req.mfa_token)
    if not sess or sess.get("authenticated"):
        raise HTTPException(status_code=400, detail="MFA session expired — please log in again")

    rs = sess["requests_session"]
    cloud = sess["cloud_host"]
    email = sess["email"]
    password = sess["password"]

    r = await mist_client.do_login(rs, cloud, email, password, two_factor=req.code)
    if not r.ok:
        raise HTTPException(status_code=401, detail="Invalid MFA code")

    self_data = await mist_client.get_self(rs, cloud)
    if self_data.get("two_factor_required") and not self_data.get("two_factor_passed"):
        raise HTTPException(status_code=401, detail="Invalid verification code")

    orgs = mist_client.parse_orgs(self_data)
    if not orgs:
        raise HTTPException(status_code=403, detail="No organisation access found")

    user_name = self_data.get("name", email)
    org_id = orgs[0]["id"] if len(orgs) == 1 else None

    sess["authenticated"] = True
    sess["password"] = ""
    sess["user_name"] = user_name
    sess["orgs"] = orgs
    if org_id:
        sess["org_id"] = org_id

    response.set_cookie(SESSION_COOKIE, req.mfa_token, max_age=28800, **COOKIE_OPTS)
    return {
        "orgs": orgs,
        "org_id": org_id,
        "user": {"email": email, "name": user_name},
    }


@router.post("/org")
async def select_org(req: OrgSelectRequest, response: Response, hd_session: Optional[str] = Cookie(None)):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess or not sess.get("authenticated"):
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
    if not sess or not sess.get("authenticated"):
        raise HTTPException(status_code=401, detail="Session expired")
    return {
        "user": {"email": sess.get("email"), "name": sess.get("user_name")},
        "orgs": sess.get("orgs"),
        "org_id": sess.get("org_id"),
    }


@router.post("/logout")
async def logout(response: Response, hd_session: Optional[str] = Cookie(None)):
    if hd_session:
        sess = get_session(hd_session)
        if sess:
            rs = sess.get("requests_session")
            cloud = sess.get("cloud_host")
            if rs and cloud:
                await mist_client.do_logout(rs, cloud)
        delete_session(hd_session)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}
