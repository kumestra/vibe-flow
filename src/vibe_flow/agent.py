"""
Agent loop.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → return response → done

Tool calls within a turn run serially, one at a time.
Uses litellm for provider-agnostic async LLM calls.
"""

import json
import os
from collections.abc import Callable
from typing import Any

import litellm
from dotenv import load_dotenv
from litellm import acompletion

from vibe_flow.logger import SessionLogger
from vibe_flow.system_prompt import build_system_prompt
from vibe_flow.tool_base import ToolResult, ToolUseContext
from vibe_flow.tool_runner import run_tool_use
from vibe_flow.tools import TOOLS_BY_NAME, get_schemas

load_dotenv()
MODEL: str = "gpt-4o"


async def query(
    user_input: str,
    messages: list[dict[str, Any]],
    logger: SessionLogger,
    on_token: Callable[[str], None] | None = None,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
    on_tool_result: Callable[[str, str], None] | None = None,
) -> str:
    """
    Run one user turn — mirrors query() in query.ts.

        while true:
            response = await call_llm(messages, tools)
            if no tool calls: return response text
            execute tools serially, append results
            loop
    """
    messages.append({"role": "user", "content": user_input})
    logger.log_user(user_input)

    ctx: ToolUseContext = ToolUseContext(
        messages=messages,
        cwd=os.getcwd(),
    )

    while True:
        # 1. Call the LLM
        system_msg: dict[str, Any] = {
            "role": "system",
            "content": build_system_prompt(),
        }
        tools: list[Any] = get_schemas()
        logger.log_llm_request(messages, tools)

        stream: Any = await acompletion(
            model=MODEL,
            tools=tools,
            messages=[system_msg] + messages,
            stream=True,
        )

        # Collect chunks; call on_token for each text token
        chunks: list[Any] = []
        async for chunk in stream:
            chunks.append(chunk)
            token: str = chunk.choices[0].delta.content or ""
            if token and on_token:
                on_token(token)

        # Reconstruct the full message from chunks
        response: Any = litellm.stream_chunk_builder(chunks)
        message: Any = response.choices[0].message
        event_id: int = logger.log_llm_response(message)

        # 2. Append assistant response to history
        messages.append(message)

        # 3. No tool calls → return the final text
        if not message.tool_calls:
            final: str = message.content or ""
            logger.log_assistant(final)
            return final

        # 4. Execute tool calls serially
        for tc in message.tool_calls:
            input_args: dict[str, Any] = json.loads(
                tc.function.arguments
            )
            if on_tool_call:
                on_tool_call(tc.function.name, input_args)
            result: ToolResult = run_tool_use(tc, ctx, TOOLS_BY_NAME)
            if on_tool_result:
                on_tool_result(tc.function.name, result.for_assistant)
            logger.log_tool(
                event_id, tc.function.name,
                input_args, result.for_assistant,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result.for_assistant,
                }
            )
