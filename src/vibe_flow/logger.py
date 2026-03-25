import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log to project_root/logs/app.log
_log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
_log_file = _log_dir / "app.log"

logger = logging.getLogger("vibe_flow")
logger.setLevel(logging.DEBUG)

# Console: INFO and above
_console = logging.StreamHandler()
_console.setLevel(logging.INFO)
_console.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(_console)

# File: DEBUG and above
if _log_dir.exists():
    _file = RotatingFileHandler(_log_file, maxBytes=1_000_000, backupCount=3)
    _file.setLevel(logging.DEBUG)
    _file.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s")
    )
    logger.addHandler(_file)
