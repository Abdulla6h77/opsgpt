import logging
import logging.config
import re

from .config import settings


SECRET_PATTERNS = [
    re.compile(r"(x-api-key=)([^&\s]+)", re.IGNORECASE),
    re.compile(r"(authorization:\s*bearer\s+)([^\s]+)", re.IGNORECASE),
]


class SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern in SECRET_PATTERNS:
            message = pattern.sub(r"\1***", message)
        record.msg = message
        record.args = ()
        return True


def configure_logging() -> None:
    level = settings.log_level.upper()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["mask_secrets"],
                }
            },
            "filters": {
                "mask_secrets": {"()": SecretMaskingFilter},
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )
