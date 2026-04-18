"""
Agent loop.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → return response → done

Tool calls within a turn run serially, one at a time.
Uses litellm for provider-agnostic async LLM calls.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import litellm
from dotenv import load_dotenv
from litellm import acompletion
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import Message, ModelResponse

from vibe_flow.logger import session_logger
from vibe_flow.system_prompt import build_system_prompt
from vibe_flow.tool_base import ToolResult, run_tool_use
from vibe_flow.tools import TOOLS_BY_NAME, get_schemas

load_dotenv()
MODEL: str = "gpt-4o"


@dataclass
class LLMRequest:
    model: str
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]]
    stream: bool


async def query(
    user_input: str,
    messages: list[dict[str, Any]],
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
    session_logger.log_user(user_input)

    while True:
        # 1. Call the LLM
        request: LLMRequest = LLMRequest(
            model=MODEL,
            messages=[{"role": "system", "content": build_system_prompt()}]
                     + messages,
            tools=get_schemas(),
            stream=True,
        )
        session_logger.log_llm_request(request)

        stream: CustomStreamWrapper = await acompletion(
            model=request.model,
            tools=request.tools,
            messages=request.messages,
            stream=request.stream,
        )

        # Collect chunks; call on_token for each text token
        chunks: list[ModelResponse] = []
        async for chunk in stream:
            chunks.append(chunk)
            token: str = chunk.choices[0].delta.content or ""
            if token and on_token:
                on_token(token)

        # Reconstruct the full message from chunks
        response: ModelResponse = litellm.stream_chunk_builder(chunks)
        event_id: int = session_logger.log_llm_response(response)
        message: Message = response.choices[0].message

        # 2. Append assistant response to history
        messages.append(message)

        # 3. No tool calls → return the final text
        if not message.tool_calls:
            final: str = message.content or ""
            session_logger.log_assistant(final)
            return final

        # 4. Execute tool calls serially
        for tc in message.tool_calls:
            input_args: dict[str, Any] = json.loads(
                tc.function.arguments
            )
            if on_tool_call:
                on_tool_call(tc.function.name, input_args)
            result: ToolResult = await run_tool_use(tc, TOOLS_BY_NAME)
            if on_tool_result:
                on_tool_result(tc.function.name, result.for_assistant)
            session_logger.log_tool(
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
