from fastapi import APIRouter, HTTPException
from ..config import load_config
from ..models import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(req: LoginRequest):
    """Verify user PIN and return user info."""
    config = load_config()
    for user in config.users:
        if user.name == req.user:
            if user.pin == req.pin:
                return {
                    "success": True,
                    "user": {
                        "name": user.name,
                        "light_ids": user.light_ids,
                    },
                }
            else:
                raise HTTPException(status_code=401, detail="Incorrect PIN")
    raise HTTPException(status_code=404, detail="User not found")
