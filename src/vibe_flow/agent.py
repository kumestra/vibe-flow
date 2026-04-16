"""
Agent loop.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → return response → done

Tool calls within a turn run serially, one at a time.
Uses AsyncOpenAI so callers can await without blocking the event loop.
"""

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from vibe_flow.logger import SessionLogger
from vibe_flow.system_prompt import build_system_prompt
from vibe_flow.tool_base import ToolResult, ToolUseContext
from vibe_flow.tool_runner import run_tool_use
from vibe_flow.tools import TOOLS_BY_NAME, get_schemas

load_dotenv()
client: AsyncOpenAI = AsyncOpenAI()
MODEL: str = "gpt-4o"


async def query(
    user_input: str,
    messages: list[ChatCompletionMessageParam],
    logger: SessionLogger,
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
        system_msg: ChatCompletionMessageParam = {
            "role": "system",
            "content": build_system_prompt(),
        }
        tools: list[Any] = get_schemas()
        logger.log_llm_request(messages, tools)

        response: Any = await client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=[system_msg] + messages,
        )

        message: Any = response.choices[0].message
        logger.log_llm_response(message)

        # 2. Append assistant response to history
        messages.append(message)

        # 3. No tool calls → return the final text
        if not message.tool_calls:
            final: str = message.content or ""
            logger.log_assistant(final)
            return final

        # 4. Execute tool calls serially
        tc: ChatCompletionMessageToolCall
        for tc in message.tool_calls:
            input_args: dict[str, Any] = json.loads(
                tc.function.arguments
            )
            logger.log_tool_call(tc.function.name, input_args)

            result: ToolResult = run_tool_use(tc, ctx, TOOLS_BY_NAME)
            logger.log_tool_result(
                tc.function.name, result.for_assistant
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result.for_assistant,
                }
            )
