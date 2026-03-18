def calculate_severity(log):
    score = 0

    if log.get("latency_ms", 0) > 2000:
        score += 3
    elif log.get("latency_ms", 0) > 800:
        score += 2

    if 500 <= log.get("status_code", 0) < 600:
        score += 3
    elif 400 <= log.get("status_code", 0) < 500:
        score += 1

    if log.get("level") == "ERROR":
        score += 2

    # Convert score to label
    if score >= 6:
        return "CRITICAL"
    elif score >= 4:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    else:
        return "LOW"