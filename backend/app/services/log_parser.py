import json
import logging

from ..schemas.log_schema import LogEntry

logger = logging.getLogger(__name__)


def _parse_log_line(line: str) -> dict | None:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        logger.warning("Failed to parse log line: %.120s", line)
        return None


def parse_logs(raw_logs: str) -> list[LogEntry]:
    parsed_logs: list[LogEntry] = []

    for line in raw_logs.splitlines():
        log_dict = _parse_log_line(line)
        if log_dict is None:
            continue
        parsed_logs.append(LogEntry(**log_dict))

    return parsed_logs
