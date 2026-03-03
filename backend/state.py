import asyncio
from .hue import HueBridge
from .sse import SSEManager

# Shared application state
bridge = HueBridge()
sse_manager = SSEManager()
event_task: asyncio.Task | None = None
