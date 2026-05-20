from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
import mist_client
from session_store import get_session
from runbooks import get_suggested_queries, ISSUE_CATEGORIES, ESCALATION_GUIDANCE

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class SuggestionsRequest(BaseModel):
    category_id: str
    client: Optional[str] = None
    site: Optional[str] = None
    timeframe: Optional[str] = "today"


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
    try:
        result = await mist_client.marvis_query(rs, cloud, sess["org_id"], req.query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Marvis error: {e}")
    return result


@router.post("/suggestions")
async def suggestions(req: SuggestionsRequest):
    queries = get_suggested_queries(
        req.category_id,
        client=req.client,
        site=req.site,
        timeframe=req.timeframe,
    )
    escalation = ESCALATION_GUIDANCE.get(req.category_id)
    return {"queries": queries, "escalation_guidance": escalation}


@router.get("/categories")
async def categories():
    return {"categories": ISSUE_CATEGORIES}
