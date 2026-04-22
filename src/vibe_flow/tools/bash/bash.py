import asyncio
from typing import Any

from vibe_flow.tool_base import Tool, ToolResult

DEFAULT_TIMEOUT_SECONDS: int = 30
MAX_TIMEOUT_SECONDS: int = 120
MAX_STREAM_BYTES: int = 10_000


def _truncate(data: bytes, limit: int = MAX_STREAM_BYTES) -> str:
    if len(data) <= limit:
        return data.decode("utf-8", errors="replace")
    head: bytes = data[:limit]
    dropped: int = len(data) - limit
    return (
        head.decode("utf-8", errors="replace")
        + f"\n[truncated {dropped} bytes]"
    )


class BashTool(Tool):
    name = "bash"
    description = (
        "Execute a shell command via /bin/sh -c. Each call runs in a "
        "fresh subprocess; working directory and environment changes "
        "do not persist between calls. Returns exit code, stdout, and "
        "stderr. Use for running tests, git, grep, build commands, "
        "etc."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": (
                    "Shell command to execute. Supports pipes, "
                    "redirects, and '&&'/'||' chaining."
                ),
            },
            "timeout_seconds": {
                "type": "integer",
                "description": (
                    "Kill the command after this many seconds. "
                    f"Default {DEFAULT_TIMEOUT_SECONDS}, max "
                    f"{MAX_TIMEOUT_SECONDS}."
                ),
            },
        },
        "required": ["command"],
    }
    requires_permission: bool = True

    async def call(self, args: dict[str, Any]) -> ToolResult:
        command: str = args["command"]
        requested_timeout: int = int(
            args.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
        )
        timeout: int = max(
            1, min(requested_timeout, MAX_TIMEOUT_SECONDS)
        )

        proc: asyncio.subprocess.Process = (
            await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ToolResult.of(
                f"Error: command timed out after {timeout}s."
            )

        exit_code: int | None = proc.returncode
        stdout_text: str = _truncate(stdout_bytes)
        stderr_text: str = _truncate(stderr_bytes)
        output: str = (
            f"exit_code: {exit_code}\n"
            f"{stdout_text}\n"
            f"---stderr---\n"
            f"{stderr_text}"
        )
        return ToolResult.of(output)


tool: BashTool = BashTool()
