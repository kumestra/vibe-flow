"""Verify that scratch experiments can import from:
1. Local files in the same folder
2. Project core code (vibe_flow)
3. Third-party libraries
"""

import sys

print("=== sys.path ===")
for i, p in enumerate(sys.path):
    print(f"  [{i}] {p or '(empty string = cwd)'}")

# 1. Local import
from helper import greet, PI

print("=== Local import ===")
print(greet("scratch"))
print(f"PI = {PI}")

# 2. Project core import
from vibe_flow.cli import main as cli_main

print("\n=== Project import ===")
cli_main()

# 3. Third-party import
from pydantic import BaseModel

class Demo(BaseModel):
    name: str
    value: int

demo = Demo(name="test", value=42)
print(f"\n=== Third-party import ===")
print(f"pydantic model: {demo}")

print("\n✅ All imports work!")
