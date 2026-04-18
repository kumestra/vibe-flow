"""
Dev MCP server — HTTP/SSE transport on localhost:8000.

Exposes tools useful during AI agent development.
Connect from any MCP client at http://localhost:8000/sse.

Run:
    uv run scripts/mcp_server.py
"""

import random

from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("dev-tools")

_CONDITIONS: list[str] = [
    "Sunny", "Partly cloudy", "Overcast",
    "Light rain", "Thunderstorm", "Snowing",
]


@mcp.tool()
def get_weather(city: str) -> str:
    """Return current weather for a city. Data is simulated."""
    condition: str = random.choice(_CONDITIONS)
    temp_c: int = random.randint(-5, 38)
    humidity: int = random.randint(20, 95)
    wind_kmh: int = random.randint(0, 80)
    return (
        f"City: {city}\n"
        f"Condition: {condition}\n"
        f"Temperature: {temp_c}°C\n"
        f"Humidity: {humidity}%\n"
        f"Wind: {wind_kmh} km/h"
    )


if __name__ == "__main__":
    mcp.run(transport="sse")
