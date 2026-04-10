"""
Minimal agent loop — the core of how Claude Code works, using OpenAI API.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → print response → done
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from src.system_prompt import build_system_prompt
from src.tool_base import ToolUseContext
from src.tool_runner import run_tool_use
from src.tools import TOOLS_BY_NAME, get_schemas

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o"


def agent_loop(user_input: str, messages: list):
    """
    The core loop — mirrors query.ts:

        while true:
            response = call_llm(messages, tools)
            if no tool calls: return response
            execute tools, append results
            loop
    """
    messages.append({"role": "user", "content": user_input})

    # One ToolUseContext per turn. Phase 2+ will populate this further
    # (abort signal, permissions, hooks, budget, etc.).
    ctx = ToolUseContext(messages=messages, cwd=os.getcwd())

    while True:
        # 1. Call the LLM
        system_msg = {"role": "system", "content": build_system_prompt()}
        response = client.chat.completions.create(
            model=MODEL,
            tools=get_schemas(),
            messages=[system_msg] + messages,
        )

        message = response.choices[0].message

        # 2. Append assistant response to history
        messages.append(message)

        # 3. Check if there are tool calls — if not, we're done
        if not message.tool_calls:
            if message.content:
                print(f"\n{message.content}")
            return

        # 4. Execute each tool call through the pipeline
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args_preview = tool_call.function.arguments[:80]
            print(f"  [tool] {name}({args_preview})")

            result = run_tool_use(tool_call, ctx, TOOLS_BY_NAME)

            # 5. Append tool result and loop back
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.for_assistant,
                }
            )


def main():
    print("Minimal Agent (type 'quit' to exit)")
    print("-" * 45)

    messages = []

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break

        try:
            agent_loop(user_input, messages)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
