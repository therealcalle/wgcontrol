import httpx
import json
from typing import Optional, AsyncGenerator


class HueBridge:
    """Client for the Philips Hue Bridge CLIP v2 API."""

    def __init__(self, ip: str = None, api_key: str = None):
        self.ip = ip
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=f"https://{self.ip}",
                headers={"hue-application-key": self.api_key},
                verify=False,
                timeout=10.0,
            )
        return self._client

    @staticmethod
    async def discover() -> list[dict]:
        """Discover Hue bridges on the network via meethue.com."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://discovery.meethue.com/")
                return resp.json()
        except Exception:
            return []

    async def pair(self) -> dict:
        """
        Pair with the bridge. User must press the bridge button first.
        Returns {"api_key": "..."} on success or {"error": "..."} on failure.
        """
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            resp = await client.post(
                f"https://{self.ip}/api",
                json={
                    "devicetype": "wgcontrol#server",
                    "generateclientkey": True,
                },
            )
            result = resp.json()
            if isinstance(result, list):
                result = result[0]
            if "error" in result:
                return {"error": result["error"]["description"]}
            if "success" in result:
                self.api_key = result["success"]["username"]
                return {"api_key": self.api_key}
            return {"error": "Unexpected response from bridge"}

    async def get_lights(self) -> list[dict]:
        """Get all lights from the bridge."""
        client = await self._get_client()
        resp = await client.get("/clip/v2/resource/light")
        data = resp.json()
        return data.get("data", [])

    async def get_light(self, light_id: str) -> Optional[dict]:
        """Get a single light by ID."""
        client = await self._get_client()
        resp = await client.get(f"/clip/v2/resource/light/{light_id}")
        data = resp.json()
        items = data.get("data", [])
        return items[0] if items else None

    async def set_light_state(self, light_id: str, state: dict) -> dict:
        """Set light state. Accepts: on, brightness, color_xy, color_temp."""
        client = await self._get_client()
        body = {}
        if "on" in state:
            body["on"] = {"on": state["on"]}
        if "brightness" in state:
            body["dimming"] = {"brightness": state["brightness"]}
        if "color_xy" in state and state["color_xy"]:
            body["color"] = {
                "xy": {"x": state["color_xy"][0], "y": state["color_xy"][1]}
            }
        if "color_temp" in state and state["color_temp"]:
            body["color_temperature"] = {"mirek": state["color_temp"]}
        resp = await client.put(
            f"/clip/v2/resource/light/{light_id}", json=body
        )
        return resp.json()

    async def event_stream(self) -> AsyncGenerator[list, None]:
        """
        Subscribe to Hue EventStream (SSE).
        Yields parsed JSON event arrays.
        """
        async with httpx.AsyncClient(
            base_url=f"https://{self.ip}",
            headers={
                "hue-application-key": self.api_key,
                "Accept": "text/event-stream",
            },
            verify=False,
            timeout=None,
        ) as client:
            async with client.stream("GET", "/eventstream/clip/v2") as resp:
                buffer = ""
                async for chunk in resp.aiter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        event_str, buffer = buffer.split("\n\n", 1)
                        for line in event_str.split("\n"):
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    yield data
                                except json.JSONDecodeError:
                                    pass

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
