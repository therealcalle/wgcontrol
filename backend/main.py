import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import load_config
from . import state
from .routes.bridge import router as bridge_router
from .routes.auth import router as auth_router
from .routes.lights import router as lights_router
from .routes.lights import normalize_light
from .routes.config_routes import router as config_router
from .routes.scenes import router as scenes_router
from .routes.events import router as events_router

logger = logging.getLogger("wgcontrol")

# Suppress insecure request warnings for Hue bridge self-signed cert
import warnings
import logging as _logging
_logging.getLogger("httpx").setLevel(_logging.WARNING)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


async def hue_event_listener():
    """Background task: listen to Hue EventStream and relay to frontend SSE."""
    while True:
        try:
            logger.info("Connecting to Hue EventStream...")
            async for events in state.bridge.event_stream():
                if isinstance(events, list):
                    for event in events:
                        if event.get("type") == "update":
                            for item in event.get("data", []):
                                if item.get("type") == "light":
                                    light_data = _normalize_event(item)
                                    await state.sse_manager.broadcast(
                                        {
                                            "type": "light_update",
                                            "id": item["id"],
                                            "state": light_data,
                                        }
                                    )
        except asyncio.CancelledError:
            logger.info("EventStream listener cancelled")
            break
        except Exception as e:
            logger.warning(f"EventStream error: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)


def _normalize_event(item: dict) -> dict:
    """Normalize a Hue event item into our light state format."""
    data = {}
    if "on" in item:
        data["on"] = item["on"].get("on")
    if "dimming" in item:
        data["brightness"] = item["dimming"].get("brightness")
    if "color" in item:
        xy = item["color"].get("xy", {})
        data["color_xy"] = {"x": xy.get("x", 0), "y": xy.get("y", 0)}
    if "color_temperature" in item:
        data["color_temp"] = item["color_temperature"].get("mirek")
    return data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = load_config()
    if config.bridge.ip and config.bridge.api_key:
        state.bridge.ip = config.bridge.ip
        state.bridge.api_key = config.bridge.api_key
        state.event_task = asyncio.create_task(hue_event_listener())
        logger.info(f"Connected to Hue bridge at {config.bridge.ip}")
    else:
        logger.info("No bridge configured — waiting for setup")

    yield

    # Shutdown
    if state.event_task:
        state.event_task.cancel()
        try:
            await state.event_task
        except asyncio.CancelledError:
            pass
    await state.bridge.close()


app = FastAPI(title="wgControl", lifespan=lifespan)

# CORS for development (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(bridge_router)
app.include_router(auth_router)
app.include_router(lights_router)
app.include_router(config_router)
app.include_router(scenes_router)
app.include_router(events_router)


# --- Startup event stream after bridge pairing ---

@app.post("/api/bridge/start-events")
async def start_event_stream():
    """Start the event stream listener (called after initial setup)."""
    if state.event_task and not state.event_task.done():
        return {"status": "already_running"}
    if state.bridge.ip and state.bridge.api_key:
        state.event_task = asyncio.create_task(hue_event_listener())
        return {"status": "started"}
    return {"status": "bridge_not_configured"}


# --- Serve frontend static files ---

static_dir = Path(__file__).parent / "static"


@app.get("/")
async def serve_index():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """SPA fallback — serve static files or index.html for client routes."""
    if full_path.startswith("api"):
        return {"detail": "Not found"}
    file_path = static_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}
