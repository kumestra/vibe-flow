def call(arguments: dict) -> str:
    with open(arguments["path"], "w") as f:
        f.write(arguments["content"])
    return f"Wrote {len(arguments['content'])} bytes to {arguments['path']}"


schema = {
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
}

tool = {"name": "write_file", "schema": schema, "call": call}
