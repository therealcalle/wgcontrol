from pydantic import BaseModel
from typing import Optional


class BridgeConfig(BaseModel):
    ip: Optional[str] = None
    api_key: Optional[str] = None


class UserConfig(BaseModel):
    name: str
    pin: str
    light_ids: list[str] = []


class SceneState(BaseModel):
    on: Optional[bool] = None
    brightness: Optional[float] = None
    color_xy: Optional[list[float]] = None
    color_temp: Optional[int] = None


class Scene(BaseModel):
    id: str
    name: str
    user: Optional[str] = None
    lights: dict[str, SceneState] = {}


class Group(BaseModel):
    id: str
    name: str
    light_ids: list[str] = []
    users: list[str] = []


class AppConfig(BaseModel):
    bridge: BridgeConfig = BridgeConfig()
    users: list[UserConfig] = []
    shared_light_ids: list[str] = []
    custom_names: dict[str, str] = {}
    scenes: list[Scene] = []
    groups: list[Group] = []


# --- Request/Response models ---

class LightStateRequest(BaseModel):
    on: Optional[bool] = None
    brightness: Optional[float] = None
    color_xy: Optional[list[float]] = None
    color_temp: Optional[int] = None


class LoginRequest(BaseModel):
    user: str
    pin: str


class PairRequest(BaseModel):
    ip: str


class UsersSetupRequest(BaseModel):
    users: list[UserConfig]


class AssignRequest(BaseModel):
    user_lights: dict[str, list[str]] = {}
    shared: list[str] = []


class CustomNameRequest(BaseModel):
    name: str


class GroupCreateRequest(BaseModel):
    name: str
    light_ids: list[str] = []
    users: list[str] = []


class SceneCreateRequest(BaseModel):
    name: str
    light_ids: list[str] = []
