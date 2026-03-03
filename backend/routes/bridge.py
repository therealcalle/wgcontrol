from fastapi import APIRouter, HTTPException
from ..config import load_config, save_config
from ..models import PairRequest
from .. import state

router = APIRouter(prefix="/api/bridge", tags=["bridge"])


@router.get("/status")
async def bridge_status():
    """Check if the bridge is configured and return basic info."""
    config = load_config()
    configured = bool(config.bridge.ip and config.bridge.api_key)
    user_names = [u.name for u in config.users]
    return {
        "configured": configured,
        "users": user_names,
        "has_users": len(user_names) > 0,
    }


@router.get("/discover")
async def discover_bridges():
    """Discover Hue bridges on the network."""
    from ..hue import HueBridge

    bridges = await HueBridge.discover()
    return {"bridges": bridges}


@router.post("/pair")
async def pair_bridge(req: PairRequest):
    """
    Pair with a Hue bridge. The user must press the bridge button first.
    Saves the bridge IP and API key to config on success.
    """
    state.bridge.ip = req.ip
    result = await state.bridge.pair()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Save to config
    config = load_config()
    config.bridge.ip = req.ip
    config.bridge.api_key = result["api_key"]
    save_config(config)

    return {"success": True, "api_key": result["api_key"]}
