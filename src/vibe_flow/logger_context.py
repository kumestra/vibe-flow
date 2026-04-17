"""
Global session logger instance.

One process = one session. Initialized at import time and shared
across the entire process without passing through function signatures.
"""

import os
import uuid

from vibe_flow.logger import SessionLogger

session_logger: SessionLogger = SessionLogger(
    str(uuid.uuid4()), os.getcwd()
)
