from collections import Counter

def generate_incident_report(anomalies):
    if not anomalies:
        return {"message": "No incidents detected."}

    total = len(anomalies)

    # Count services
    services = [log["service"] for log in anomalies]
    service_counts = Counter(services)

    # Find most affected service
    most_affected = service_counts.most_common(1)[0]

    # Severity distribution
    severities = [log["severity"] for log in anomalies]
    severity_counts = Counter(severities)

    # Determine highest severity
    severity_priority = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    highest_severity = None
    for level in severity_priority:
        if level in severity_counts:
            highest_severity = level
            break

    return {
        "total_anomalies": total,
        "most_affected_service": most_affected[0],
        "service_anomaly_count": most_affected[1],
        "severity_distribution": dict(severity_counts),
        "highest_severity": highest_severity
    }

def generate_summary(report):
    if "message" in report:
        return report["message"]

    return (
        f"{report['highest_severity']} incident detected. "
        f"{report['total_anomalies']} anomalies found. "
        f"Most impacted service: {report['most_affected_service']} "
        f"({report['service_anomaly_count']} anomalies). "
        "Immediate investigation recommended."
    )