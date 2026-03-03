import uuid
from fastapi import APIRouter, HTTPException
from ..config import load_config, save_config
from ..models import (
    UsersSetupRequest,
    AssignRequest,
    CustomNameRequest,
    GroupCreateRequest,
    UserConfig,
)

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
async def get_config():
    """Get the full app config (for settings page)."""
    config = load_config()
    data = config.model_dump()
    # Don't expose PINs
    for user in data["users"]:
        user.pop("pin", None)
    return data


@router.post("/users")
async def setup_users(req: UsersSetupRequest):
    """Set up users (initial setup or update)."""
    config = load_config()
    config.users = req.users
    save_config(config)
    return {"success": True}


@router.put("/users/{username}/pin")
async def update_pin(username: str, pin: str):
    """Update a user's PIN."""
    config = load_config()
    for user in config.users:
        if user.name == username:
            user.pin = pin
            save_config(config)
            return {"success": True}
    raise HTTPException(404, "User not found")


@router.post("/assign")
async def assign_lights(req: AssignRequest):
    """Assign lights to users and shared pool."""
    config = load_config()

    # Update user light assignments
    for user in config.users:
        if user.name in req.user_lights:
            user.light_ids = req.user_lights[user.name]

    config.shared_light_ids = req.shared
    save_config(config)
    return {"success": True}


@router.put("/custom-name/{light_id}")
async def set_custom_name(light_id: str, req: CustomNameRequest):
    """Set a custom display name for a light."""
    config = load_config()
    if req.name:
        config.custom_names[light_id] = req.name
    else:
        config.custom_names.pop(light_id, None)
    save_config(config)
    return {"success": True}


# --- Groups ---

@router.get("/groups")
async def get_groups():
    """Get all groups."""
    config = load_config()
    return config.groups


@router.post("/groups")
async def create_group(req: GroupCreateRequest):
    """Create a new group."""
    from ..models import Group

    config = load_config()
    group = Group(
        id=str(uuid.uuid4()),
        name=req.name,
        light_ids=req.light_ids,
        users=req.users,
    )
    config.groups.append(group)
    save_config(config)
    return group.model_dump()


@router.put("/groups/{group_id}")
async def update_group(group_id: str, req: GroupCreateRequest):
    """Update an existing group."""
    config = load_config()
    for i, g in enumerate(config.groups):
        if g.id == group_id:
            config.groups[i].name = req.name
            config.groups[i].light_ids = req.light_ids
            config.groups[i].users = req.users
            save_config(config)
            return config.groups[i].model_dump()
    raise HTTPException(404, "Group not found")


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str):
    """Delete a group."""
    config = load_config()
    config.groups = [g for g in config.groups if g.id != group_id]
    save_config(config)
    return {"success": True}
