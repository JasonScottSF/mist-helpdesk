from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
import mist_client
from session_store import get_session
from runbooks import get_suggested_queries, ISSUE_CATEGORIES, ESCALATION_GUIDANCE

router = APIRouter()


class QueryRequest(BaseModel):
    troubleshoot_type: str          # "client", "wireless", "wired", "wan"
    mac:     Optional[str] = None   # required for troubleshoot_type="client"
    site_id: Optional[str] = None   # required for wireless/wired/wan


class SuggestionsRequest(BaseModel):
    category_id: str


def _require_session(hd_session: Optional[str]):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess or not sess.get("authenticated"):
        raise HTTPException(status_code=401, detail="Session expired")
    if not sess.get("org_id"):
        raise HTTPException(status_code=400, detail="No org selected")
    return sess


@router.post("/query")
async def query(req: QueryRequest, hd_session: Optional[str] = Cookie(None)):
    sess = _require_session(hd_session)
    rs = sess["requests_session"]
    cloud = sess["cloud_host"]

    if req.troubleshoot_type == "client" and not req.mac:
        raise HTTPException(status_code=400, detail="mac is required for client troubleshoot")
    if req.troubleshoot_type != "client" and not req.site_id:
        raise HTTPException(status_code=400, detail="site_id is required for site troubleshoot")

    try:
        result = await mist_client.marvis_troubleshoot(
            rs, cloud, sess["org_id"],
            req.troubleshoot_type,
            mac=req.mac,
            site_id=req.site_id,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Marvis error: {e}")
    return result


@router.post("/suggestions")
async def suggestions(req: SuggestionsRequest):
    queries = get_suggested_queries(req.category_id)
    escalation = ESCALATION_GUIDANCE.get(req.category_id)
    return {"queries": queries, "escalation_guidance": escalation}


@router.get("/categories")
async def categories():
    return {"categories": ISSUE_CATEGORIES}
