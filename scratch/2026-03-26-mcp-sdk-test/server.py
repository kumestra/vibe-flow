"""MCP server using the SDK — compare with the raw version."""

import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("price-server")


@mcp.tool()
def get_gold_price(date: str) -> str:
    """Get gold price per ounce in USD for a given date."""
    seed = hash(("gold", date))
    rng = random.Random(seed)  # noqa: S311
    price = round(rng.uniform(1800, 2400), 2)
    return f"Gold on {date}: ${price}/oz"


@mcp.tool()
def get_bitcoin_price(date: str) -> str:
    """Get bitcoin price in USD for a given date."""
    seed = hash(("bitcoin", date))
    rng = random.Random(seed)  # noqa: S311
    price = round(rng.uniform(50000, 100000), 2)
    return f"Bitcoin on {date}: ${price}"


if __name__ == "__main__":
    mcp.run(transport="sse")
