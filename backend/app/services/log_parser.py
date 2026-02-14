import ast
from typing import List
from ..schemas.log_schema import LogEntry


def parse_logs(raw_logs: str) -> List[LogEntry]:
    parsed_logs = []

    for line in raw_logs.splitlines():
        try:
            log_dict = ast.literal_eval(line)
            parsed_logs.append(LogEntry(**log_dict))
        except Exception:
            continue

    return parsed_logs
