from fastapi import APIRouter, UploadFile, File
from ..services.log_parser import parse_logs
from ..services.anomaly_client import detect_anomalies
from ai.explain import explain_anomaly
from ai.severity import calculate_severity
from ai.incident import generate_incident_report, generate_summary
from ai.remediation import suggest_fix

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    raw = await file.read()
    logs = parse_logs(raw.decode("utf-8"))

    anomalies = detect_anomalies([log.dict() for log in logs])

    # Add explanation and severity for every detected anomaly before reporting.
    
    for log in anomalies:
        log["explanation"] = explain_anomaly(log)
        log["severity"] = calculate_severity(log)

        remediation = suggest_fix(log)
        log["root_cause"] = remediation["root_cause"]
        log["suggested_fix"] = remediation["suggested_fix"]

    report = generate_incident_report(anomalies)
    summary = generate_summary(report)

    return {
        "total_logs": len(logs),
        "anomalies_detected": len(anomalies),
        "incident_report": report,
        "incident_summary": summary,
        "anomalies": anomalies[:20],
    }
