"""CLI chatbot with clean separation: chat loop + tool router.

Chat loop doesn't know about MCP, HTTP, or how tools work.
It just calls router.call(name, args).
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from tool_router import ToolRouter

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# --- Chat loop (core) ---


def chat_loop(client: OpenAI, router: ToolRouter) -> None:
    """Run the chat loop. Only knows about LLM and router.call()."""
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    print(f"\nChatbot ready (model: {MODEL}). Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        tools = router.get_openai_tools()

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        assistant_msg = response.choices[0].message

        # Handle tool calls
        while assistant_msg.tool_calls:
            messages.append(assistant_msg.model_dump())
            for tool_call in assistant_msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [tool] {name}({args})")

                result = router.call(name, args)
                print(f"  [tool] → {result}")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    },
                )

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
            )
            assistant_msg = response.choices[0].message

        print(f"Bot: {assistant_msg.content}\n")
        messages.append({"role": "assistant", "content": assistant_msg.content})


# --- Setup (wiring) ---


def main() -> None:
    """Wire up the components and start chatting."""
    client = OpenAI()
    router = ToolRouter()

    # Connect MCP server
    print("Connecting to MCP server...")
    router.connect_mcp("http://localhost:8000")

    # Start chat
    chat_loop(client, router)


if __name__ == "__main__":
    main()
