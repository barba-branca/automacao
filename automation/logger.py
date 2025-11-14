import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(log_dir: Path):
    """
    Configures the main logger for the automation.
    Now accepts a directory path to store the log file.
    """
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("ContabilAutomation")
    logger.setLevel(logging.DEBUG)

    # Prevent propagation to the root logger and remove existing handlers
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    fh = RotatingFileHandler(
        log_dir / "automation.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)

    return logger

# This will be replaced by the instance created in main.py
# This is a placeholder for when modules are used standalone.
log = logging.getLogger("ContabilAutomation")
if not log.hasHandlers():
    log.addHandler(logging.NullHandler())
