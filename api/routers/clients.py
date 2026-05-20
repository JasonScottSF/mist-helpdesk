from fastapi import APIRouter, Cookie, HTTPException
from typing import Optional
import mist_client
from session_store import get_session

router = APIRouter()

WIRELESS_FIELDS = ["mac", "ip", "hostname", "username", "family", "os", "model",
                   "ap_mac", "ssid", "rssi", "uptime", "last_seen"]
WIRED_FIELDS    = ["mac", "ip", "hostname", "port_id", "vlan_id", "vlan_name", "manufacture"]


def _require_session(hd_session: Optional[str]):
    if not hd_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sess = get_session(hd_session)
    if not sess or not sess.get("authenticated"):
        raise HTTPException(status_code=401, detail="Session expired")
    return sess


def _slim(client: dict, fields: list) -> dict:
    return {k: client.get(k) for k in fields if client.get(k) is not None}


@router.get("/{site_id}/wireless")
async def wireless_clients(site_id: str, hd_session: Optional[str] = Cookie(None)):
    sess = _require_session(hd_session)
    rs = sess["requests_session"]
    cloud = sess["cloud_host"]
    try:
        clients = await mist_client.get_wireless_clients(rs, cloud, site_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mist API error: {e}")
    return {"clients": [_slim(c, WIRELESS_FIELDS) for c in clients]}


@router.get("/{site_id}/wired")
async def wired_clients(site_id: str, hd_session: Optional[str] = Cookie(None)):
    sess = _require_session(hd_session)
    rs = sess["requests_session"]
    cloud = sess["cloud_host"]
    try:
        clients = await mist_client.get_wired_clients(rs, cloud, sess["org_id"], site_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mist API error: {e}")
    return {"clients": [_slim(c, WIRED_FIELDS) for c in clients]}
