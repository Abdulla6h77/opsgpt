export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Incident {
  id: string;
  service: string;
  severity: Severity;
  status: string;
  summary: string;
  root_cause: string;
  remediation: string;
  created_at: string;
  updated_at?: string;
}

export interface Anomaly {
  timestamp: string;
  service: string;
  message: string;
  severity: Severity;
  latency_ms: number;
  status_code: number;
  root_cause?: string;
  suggested_fix?: string;
}

export interface IncidentSummary {
  total_incidents: number;
  critical_incidents: number;
  services_affected: number;
  total_anomalies: number;
}

export interface IncidentListResponse {
  total: number;
  limit: number;
  offset: number;
  items: Incident[];
}

export interface DetectAnomaliesResponse {
  total_logs: number;
  anomalies_detected: number;
  incident_report: Record<string, unknown>;
  incident_summary: string;
  anomalies: Anomaly[];
}

