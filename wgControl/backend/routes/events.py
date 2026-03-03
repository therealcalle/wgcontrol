from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from .. import state

router = APIRouter(tags=["events"])


@router.get("/api/events")
async def event_stream(request: Request):
    """SSE endpoint that streams light state changes to the frontend."""

    async def generate():
        async for data in state.sse_manager.subscribe():
            if await request.is_disconnected():
                break
            yield f"data: {data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
