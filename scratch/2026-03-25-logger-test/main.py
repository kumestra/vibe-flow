"""Test that the shared logger works from scratch code."""

from vibe_flow.logger import logger

logger.debug("debug message - file only")
logger.info("info message - console and file")
logger.warning("warning message - console and file")

print("\nCheck logs/app.log for all messages including debug.")
