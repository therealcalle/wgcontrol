import asyncio
import json
from asyncio import Queue


class SSEManager:
    """Manages Server-Sent Events connections to frontend clients."""

    def __init__(self):
        self._queues: set[Queue] = set()

    async def subscribe(self):
        """Subscribe to events. Yields JSON strings."""
        queue: Queue = Queue(maxsize=100)
        self._queues.add(queue)
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            pass
        finally:
            self._queues.discard(queue)

    async def broadcast(self, event: dict):
        """Broadcast an event to all connected clients."""
        data = json.dumps(event)
        dead = set()
        for queue in self._queues:
            try:
                queue.put_nowait(data)
            except asyncio.QueueFull:
                dead.add(queue)
        self._queues -= dead

    @property
    def client_count(self) -> int:
        return len(self._queues)
