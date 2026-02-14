def explain_anomaly(log):
    reasons = []

    latency = log.get("latency_ms", 0)
    status = log.get("status_code", 0)
    level = log.get("level", "")
    service = log.get("service", "")
    message = log.get("message", "").lower()

    # Latency analysis
    if latency > 2000:
        reasons.append("Extremely high latency (>2000ms) detected")
    elif latency > 800:
        reasons.append("High latency spike detected")

    # Status code analysis
    if 500 <= status < 600:
        reasons.append(f"Server returned {status} (5xx failure)")
    elif 400 <= status < 500:
        reasons.append(f"Client error detected ({status})")

    # Message-based reasoning
    if "timeout" in message:
        reasons.append("Timeout detected in service communication")

    if "database" in message:
        reasons.append("Database-related failure")

    if "unhandled exception" in message:
        reasons.append("Unhandled exception occurred")

    # Service-aware reasoning
    if service == "auth-service" and status == 503:
        reasons.append("Authentication service likely overloaded")

    if service == "api-gateway" and status == 500:
        reasons.append("Gateway failed to route request properly")

    # Fallback
    if not reasons:
        reasons.append("Unusual behavior detected by anomaly model")

    return reasons