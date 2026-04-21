"""
MCP client — connects to an SSE MCP server and exposes its tools.

Usage:
    stack = AsyncExitStack()
    tools = await load_mcp_tools("http://localhost:8000/sse", stack)
    # tools is a list[Tool] ready to register in the tool registry
    # call stack.aclose() when done (e.g. on app shutdown)
"""

from contextlib import AsyncExitStack
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, TextContent

from vibe_flow.tool_base import Tool, ToolResult


class MCPTool(Tool):
    """
    Adapts a remote MCP tool to the local Tool ABC.
    Delegates call() to the MCP server over an open ClientSession.
    """

    requires_permission: bool = True

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        session: ClientSession,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema
        self._session: ClientSession = session

    async def call(self, args: dict[str, Any]) -> ToolResult:
        result: CallToolResult = await self._session.call_tool(
            self.name, args
        )
        text: str = "\n".join(
            block.text
            for block in result.content
            if isinstance(block, TextContent)
        )
        if result.isError:
            return ToolResult.of(f"Error from MCP tool: {text}")
        return ToolResult.of(text)


async def load_mcp_tools(
    url: str,
    exit_stack: AsyncExitStack,
) -> list[Tool]:
    """
    Connect to an MCP server at url, discover its tools, and return
    them as MCPTool instances. The connection stays open for the
    lifetime of exit_stack — call exit_stack.aclose() to disconnect.
    """
    read, write = await exit_stack.enter_async_context(sse_client(url))
    session: ClientSession = await exit_stack.enter_async_context(
        ClientSession(read, write)
    )
    await session.initialize()

    response = await session.list_tools()
    return [
        MCPTool(
            name=t.name,
            description=t.description or "",
            input_schema=t.inputSchema,
            session=session,
        )
        for t in response.tools
    ]
