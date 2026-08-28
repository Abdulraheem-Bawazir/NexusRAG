import logging

##Logging is better than print statements because it allows for different levels of severity, can be easily turned on or off, and can be directed to different outputs (console, file, etc.).## 
from app.core.config import settings

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging() -> None:
    """Configure application-wide logging."""

    log_level = getattr(
        logging,
        settings.log_level,
        logging.INFO,
    )

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
    )