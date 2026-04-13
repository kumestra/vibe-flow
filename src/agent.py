"""
Agent loop.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → print response → done

Tool calls within a turn run serially, one at a time.
"""

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from src.system_prompt import build_system_prompt
from src.tool_base import ToolResult, ToolUseContext
from src.tool_runner import run_tool_use
from src.tools import TOOLS_BY_NAME, get_schemas

load_dotenv()
client: OpenAI = OpenAI()
MODEL: str = "gpt-4o"


def query(
    user_input: str,
    messages: list[ChatCompletionMessageParam],
) -> None:
    """
    Run one user turn — mirrors query() in query.ts.

        while true:
            response = call_llm(messages, tools)
            if no tool calls: return response
            execute tools serially, append results
            loop
    """
    messages.append({"role": "user", "content": user_input})

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
        response: Any = client.chat.completions.create(
            model=MODEL,
            tools=get_schemas(),
            messages=[system_msg] + messages,
        )

        message: Any = response.choices[0].message

        # 2. Append assistant response to history
        messages.append(message)

        # 3. No tool calls → we're done
        if not message.tool_calls:
            if message.content:
                print(f"\n{message.content}")
            return

        # 4. Execute tool calls serially
        tc: ChatCompletionMessageToolCall
        for tc in message.tool_calls:
            name: str = tc.function.name
            args_preview: str = tc.function.arguments[:80]
            print(f"  [tool] {name}({args_preview})")

            result: ToolResult = run_tool_use(tc, ctx, TOOLS_BY_NAME)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result.for_assistant,
                }
            )


def main() -> None:
    print("Minimal Agent (type 'quit' to exit)")
    print("-" * 45)

    messages: list[ChatCompletionMessageParam] = []

    while True:
        try:
            user_input: str = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break

        try:
            query(user_input, messages)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
