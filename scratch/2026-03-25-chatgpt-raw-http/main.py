"""CLI chatbot using raw HTTP requests to ChatGPT with tool calling."""

import json
import os

import requests
from dotenv import load_dotenv

from vibe_flow.logger import logger

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}
MODEL = "gpt-4o-mini"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. Tokyo",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# --- Tool implementation ---


def get_weather(city):
    """Return fake weather data."""
    fake_data = {
        "tokyo": {"temp": 18, "condition": "cloudy"},
        "london": {"temp": 12, "condition": "rainy"},
        "new york": {"temp": 22, "condition": "sunny"},
    }
    weather = fake_data.get(city.lower(), {"temp": 20, "condition": "unknown"})
    return {"city": city, "temp_c": weather["temp"], "condition": weather["condition"]}


TOOL_MAP = {
    "get_weather": get_weather,
}


# --- HTTP logging ---


def log_request(req):
    """Log full HTTP request: status line, headers, body."""
    logger.debug(f">>> {req.method} {req.url} HTTP/1.1")
    for k, v in req.headers.items():
        if k.lower() == "authorization":
            v = "Bearer sk-***"
        logger.debug(f">>> {k}: {v}")
    if req.body:
        logger.debug(">>>")
        logger.debug(f">>> {json.dumps(json.loads(req.body), indent=2, ensure_ascii=False)}")


def log_response(resp):
    """Log full HTTP response: status line, headers, body."""
    logger.debug(f"<<< HTTP/{resp.raw.version / 10:.1f} {resp.status_code} {resp.reason}")
    for k, v in resp.headers.items():
        logger.debug(f"<<< {k}: {v}")
    logger.debug("<<<")
    logger.debug(f"<<< {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")


# --- API call ---


def chat(messages):
    """Send messages to ChatGPT and return the response JSON."""
    body = {"model": MODEL, "messages": messages, "tools": TOOLS}
    resp = requests.post(URL, headers=HEADERS, json=body)
    log_request(resp.request)
    log_response(resp)
    resp.raise_for_status()
    return resp.json()


# --- Main loop ---


def main():
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    print(f"Chatbot ready (model: {MODEL}). Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        data = chat(messages)
        assistant_msg = data["choices"][0]["message"]

        # Handle tool calls
        while assistant_msg.get("tool_calls"):
            messages.append(assistant_msg)
            for tool_call in assistant_msg["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                print(f"  [tool] {name}({args})")

                func = TOOL_MAP.get(name)
                result = func(**args) if func else {"error": f"unknown tool: {name}"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": name,
                    "content": json.dumps(result),
                })

            data = chat(messages)
            assistant_msg = data["choices"][0]["message"]

        reply = assistant_msg["content"]
        messages.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()
