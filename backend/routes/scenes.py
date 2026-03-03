import uuid
from fastapi import APIRouter, HTTPException
from ..config import load_config, save_config
from ..models import SceneCreateRequest, SceneState, Scene
from .. import state

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


@router.get("")
async def get_scenes(user: str = None):
    """Get scenes, optionally filtered by user."""
    config = load_config()
    scenes = config.scenes
    if user:
        scenes = [s for s in scenes if s.user is None or s.user == user]
    return [s.model_dump() for s in scenes]


@router.post("")
async def create_scene(req: SceneCreateRequest):
    """
    Create a scene from the current state of the specified lights.
    Reads current light states from the bridge.
    """
    if not state.bridge.api_key:
        raise HTTPException(503, "Bridge not configured")

    config = load_config()

    # Fetch current states of the specified lights
    light_states = {}
    for light_id in req.light_ids:
        light = await state.bridge.get_light(light_id)
        if light:
            scene_state = SceneState(
                on=light.get("on", {}).get("on"),
                brightness=light.get("dimming", {}).get("brightness"),
            )
            if "color" in light:
                xy = light["color"].get("xy", {})
                scene_state.color_xy = [xy.get("x", 0), xy.get("y", 0)]
            if "color_temperature" in light:
                scene_state.color_temp = light["color_temperature"].get("mirek")
            light_states[light_id] = scene_state

    scene = Scene(
        id=str(uuid.uuid4()),
        name=req.name,
        user=None,  # Will be set from frontend
        lights=light_states,
    )
    config.scenes.append(scene)
    save_config(config)
    return scene.model_dump()


@router.post("/{scene_id}/apply")
async def apply_scene(scene_id: str):
    """Apply a scene — set all lights to their saved states."""
    if not state.bridge.api_key:
        raise HTTPException(503, "Bridge not configured")

    config = load_config()
    scene = None
    for s in config.scenes:
        if s.id == scene_id:
            scene = s
            break
    if not scene:
        raise HTTPException(404, "Scene not found")

    results = {}
    for light_id, scene_state in scene.lights.items():
        state_dict = scene_state.model_dump(exclude_none=True)
        result = await state.bridge.set_light_state(light_id, state_dict)
        results[light_id] = result

    return {"success": True, "results": results}


@router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """Delete a scene."""
    config = load_config()
    config.scenes = [s for s in config.scenes if s.id != scene_id]
    save_config(config)
    return {"success": True}
