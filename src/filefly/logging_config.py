import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs" / "runtime"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging():
    logger = logging.getLogger()
    
    # Prevent duplicate handlers if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    # File handler (writes to file)
    file_handler = logging.FileHandler(LOG_DIR / "filefly.log")
    file_handler.setFormatter(formatter)

    # Console handler (prints to terminal)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)