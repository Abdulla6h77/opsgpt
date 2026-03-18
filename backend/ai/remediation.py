def suggest_fix(log):
    service = log.get("service", "")
    status = log.get("status_code", 0)
    message = log.get("message", "").lower()

    # Database issues
    if "database" in message:
        return {
            "root_cause": "Database connection or query failure",
            "suggested_fix": "Check DB connection pool limits or restart DB service"
        }

    # Timeout issues
    if "timeout" in message:
        return {
            "root_cause": "Service communication timeout",
            "suggested_fix": "Investigate upstream service latency or increase timeout threshold"
        }

    # 503 errors
    if status == 503:
        return {
            "root_cause": "Service overload or unavailable instance",
            "suggested_fix": "Scale horizontally or check container health"
        }

    # 500 errors
    if status == 500:
        return {
            "root_cause": "Unhandled server exception",
            "suggested_fix": "Check server logs for stack trace and patch failing handler"
        }

    return {
        "root_cause": "Unknown anomaly pattern",
        "suggested_fix": "Manual investigation required"
    }