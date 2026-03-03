from fastapi import APIRouter, HTTPException
from ..config import load_config
from ..models import LightStateRequest
from .. import state

router = APIRouter(prefix="/api/lights", tags=["lights"])


def normalize_light(light: dict, custom_names: dict = None) -> dict:
    """Extract relevant fields from a Hue API light object."""
    capabilities = []
    if "dimming" in light:
        capabilities.append("dimming")
    if "color" in light:
        capabilities.append("color")
    if "color_temperature" in light:
        capabilities.append("color_temperature")

    data = {
        "id": light["id"],
        "name": light.get("metadata", {}).get("name", "Unknown"),
        "on": light.get("on", {}).get("on", False),
        "capabilities": capabilities,
    }

    # Apply custom name if set
    if custom_names and light["id"] in custom_names:
        data["custom_name"] = custom_names[light["id"]]

    if "dimming" in light:
        data["brightness"] = light["dimming"].get("brightness", 0)

    if "color" in light:
        xy = light["color"].get("xy", {})
        data["color_xy"] = {"x": xy.get("x", 0), "y": xy.get("y", 0)}
        data["gamut"] = light["color"].get("gamut", {})
        data["gamut_type"] = light["color"].get("gamut_type", "C")

    if "color_temperature" in light:
        ct = light["color_temperature"]
        data["color_temp"] = ct.get("mirek")
        data["color_temp_range"] = {
            "min": ct.get("mirek_schema", {}).get("mirek_minimum", 153),
            "max": ct.get("mirek_schema", {}).get("mirek_maximum", 500),
        }

    return data


@router.get("/all")
async def get_all_lights():
    """Get all lights from the bridge (used during setup)."""
    if not state.bridge.api_key:
        raise HTTPException(503, "Bridge not configured")
    lights = await state.bridge.get_lights()
    return [normalize_light(l) for l in lights]


@router.get("/user/{username}")
async def get_user_lights(username: str):
    """Get lights organized for a specific user (user's + shared)."""
    if not state.bridge.api_key:
        raise HTTPException(503, "Bridge not configured")

    config = load_config()
    all_lights = await state.bridge.get_lights()

    # Find the user
    user = None
    for u in config.users:
        if u.name == username:
            user = u
            break
    if not user:
        raise HTTPException(404, "User not found")

    # Build lookup
    lights_by_id = {}
    for light in all_lights:
        lights_by_id[light["id"]] = normalize_light(light, config.custom_names)

    user_lights = [
        lights_by_id[lid]
        for lid in user.light_ids
        if lid in lights_by_id
    ]
    shared_lights = [
        lights_by_id[lid]
        for lid in config.shared_light_ids
        if lid in lights_by_id
    ]

    return {
        "user_lights": user_lights,
        "shared_lights": shared_lights,
    }


@router.put("/{light_id}")
async def update_light(light_id: str, req: LightStateRequest):
    """Update a light's state."""
    if not state.bridge.api_key:
        raise HTTPException(503, "Bridge not configured")
    state_dict = req.model_dump(exclude_none=True)
    result = await state.bridge.set_light_state(light_id, state_dict)
    return result
