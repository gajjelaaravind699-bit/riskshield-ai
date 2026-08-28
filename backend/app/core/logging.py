"""
Structured logging and sensitive data redaction filter.
"""

import json
import logging
import re
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variable for request correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id_ctx", default=None)

# Patterns / Keys representing sensitive financial and authentication data
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"pass(word)?", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[-_]?key", re.IGNORECASE),
    re.compile(r"auth(orization)?", re.IGNORECASE),
    re.compile(r"pan", re.IGNORECASE),
    re.compile(r"card[-_]?num(ber)?", re.IGNORECASE),
    re.compile(r"cvv\d?", re.IGNORECASE),
    re.compile(r"cvc\d?", re.IGNORECASE),
    re.compile(r"pin", re.IGNORECASE),
    re.compile(r"key", re.IGNORECASE),
    re.compile(r"private", re.IGNORECASE),
]

# Sensitive values patterns (e.g. 13-19 digit card numbers, Bearer tokens)
PAN_VALUE_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-_.]+", re.IGNORECASE)


def redact_sensitive_data(data: Any) -> Any:
    """
    Recursively sanitize dictionaries, lists, and strings to prevent sensitive
    credentials, PANs, CVVs, or keys from appearing in logs or error traces.
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_str = str(key)
            if any(pattern.search(key_str) for pattern in SENSITIVE_KEY_PATTERNS):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = redact_sensitive_data(value)
        return sanitized
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # Scrub potential Bearer tokens
        scrubbed = BEARER_PATTERN.sub("Bearer [REDACTED]", data)
        # Scrub potential raw PANs if length >= 13
        if len(scrubbed) >= 13:
            scrubbed = PAN_VALUE_PATTERN.sub("[REDACTED_CARD_PAN]", scrubbed)
        return scrubbed
    return data


class StructuredJsonFormatter(logging.Formatter):
    """
    Formatter that outputs structured JSON logs with correlation IDs and redaction.
    """

    def format(self, record: logging.LogRecord) -> str:
        correlation_id = correlation_id_ctx.get() or getattr(record, "correlation_id", None)
        
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive_data(record.getMessage()),
            "correlation_id": correlation_id,
        }

        # Include exception info if present
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        # Include extra attributes
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_payload["extra"] = redact_sensitive_data(record.extra)

        return json.dumps(log_payload)


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that sanitizes arguments and messages before processing.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_data(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = redact_sensitive_data(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_sensitive_data(arg) for arg in record.args)
        return True


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure root and application loggers with structured formatting and security filters.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if log_format.lower() == "json":
        formatter = StructuredJsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] [corr_id=%(correlation_id)s] %(message)s",
            defaults={"correlation_id": "-"},
        )

    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)

    # Set third-party loggers to reasonable levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
