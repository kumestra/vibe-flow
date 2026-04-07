"""
Minimal agent loop — the core of how Claude Code works, using OpenAI API.

Flow:
    user input → messages → call LLM → tool calls? → execute tools → loop
                                       → no tools?  → print response → done
"""

import json
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o"

# -- Tool definitions (OpenAI function calling format) ----------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command and return its output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to run",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
]

# -- Tool execution (what actually runs) ------------------------------------


def execute_tool(name: str, arguments: dict) -> str:
    """Run a tool and return the result as a string."""
    if name == "bash":
        result = subprocess.run(
            arguments["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n(exit code {result.returncode})"
        return output or "(no output)"

    elif name == "read_file":
        with open(arguments["path"], "r") as f:
            return f.read()

    elif name == "write_file":
        with open(arguments["path"], "w") as f:
            f.write(arguments["content"])
        return f"Wrote {len(arguments['content'])} bytes to {arguments['path']}"

    else:
        return f"Unknown tool: {name}"


# -- Core agent loop --------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. "
    "Use the provided tools to help the user with their tasks. "
    "Be concise in your responses."
)


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

    while True:
        # 1. Call the LLM
        response = client.chat.completions.create(
            model=MODEL,
            tools=TOOLS,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        )

        message = response.choices[0].message

        # 2. Append assistant response to history
        messages.append(message)

        # 3. Check if there are tool calls — if not, we're done
        if not message.tool_calls:
            if message.content:
                print(f"\n{message.content}")
            return

        # 4. Execute each tool call and collect results
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"  [tool] {name}({json.dumps(arguments, indent=None)[:80]})")

            try:
                result = execute_tool(name, arguments)
            except Exception as e:
                result = f"Error: {e}"

            # 5. Append tool result and loop back
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )


# -- REPL -------------------------------------------------------------------


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
