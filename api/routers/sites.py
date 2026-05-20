from fastapi import APIRouter, Cookie, HTTPException
from typing import Optional
import mist_client
from session_store import get_session

router = APIRouter()


def _require_session(hd_session: Optional[str]):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess or not sess.get("authenticated"):
        raise HTTPException(status_code=401, detail="Session expired")
    if not sess.get("org_id"):
        raise HTTPException(status_code=400, detail="No org selected")
    return sess


@router.get("")
async def list_sites(hd_session: Optional[str] = Cookie(None)):
    sess = _require_session(hd_session)
    rs = sess["requests_session"]
    cloud = sess["cloud_host"]
    try:
        sites = await mist_client.get_sites(rs, cloud, sess["org_id"])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mist API error: {e}")
    return {"sites": sites}
