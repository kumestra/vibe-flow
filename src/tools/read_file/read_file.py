def call(arguments: dict) -> str:
    with open(arguments["path"], "r") as f:
        return f.read()


schema = {
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
}

tool = {"name": "read_file", "schema": schema, "call": call}
