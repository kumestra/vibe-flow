import subprocess


def call(arguments: dict) -> str:
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


schema = {
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
}

tool = {"name": "bash", "schema": schema, "call": call}
