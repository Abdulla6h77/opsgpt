import {
  Anomaly,
  DetectAnomaliesResponse,
  Incident,
  IncidentListResponse
} from "@/lib/types";

async function request<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const response = await fetch(endpoint, {
    ...init,
    cache: "no-store"
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown backend error.");
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function mapIncident(raw: Record<string, unknown>): Incident {
  return {
    id: String(raw.id),
    service: String(raw.service_name ?? raw.service ?? "unknown-service"),
    severity: String(raw.severity ?? "LOW").toUpperCase() as Incident["severity"],
    status: String(raw.status ?? "OPEN"),
    summary: String(raw.summary ?? ""),
    root_cause: String(raw.root_cause ?? ""),
    remediation: String(raw.remediation ?? ""),
    created_at: String(raw.created_at ?? ""),
    updated_at: raw.updated_at ? String(raw.updated_at) : undefined
  };
}

function mapAnomaly(raw: Record<string, unknown>): Anomaly {
  return {
    timestamp: String(raw.timestamp ?? ""),
    service: String(raw.service ?? "unknown-service"),
    message: String(raw.message ?? ""),
    severity: String(raw.severity ?? "LOW").toUpperCase() as Anomaly["severity"],
    latency_ms: Number(raw.latency_ms ?? 0),
    status_code: Number(raw.status_code ?? 0),
    root_cause: raw.root_cause ? String(raw.root_cause) : undefined,
    suggested_fix: raw.suggested_fix ? String(raw.suggested_fix) : undefined
  };
}

export async function fetchIncidents(limit = 10, offset = 0): Promise<IncidentListResponse> {
  const data = await request<{
    total: number;
    limit: number;
    offset: number;
    items: Record<string, unknown>[];
  }>(`/api/incidents?limit=${limit}&offset=${offset}`);

  return {
    total: data.total,
    limit: data.limit,
    offset: data.offset,
    items: data.items.map(mapIncident)
  };
}

export async function fetchIncident(id: string): Promise<Incident> {
  try {
    const data = await request<Record<string, unknown>>(`/api/incidents/${id}`);
    return mapIncident(data);
  } catch {
    const page = await fetchIncidents(100, 0);
    const incident = page.items.find((item) => item.id === id);
    if (!incident) {
      throw new Error("Incident not found.");
    }
    return incident;
  }
}

export async function fetchAnomalies(limit = 100, offset = 0): Promise<{
  total: number;
  items: Anomaly[];
}> {
  const data = await request<{ total: number; items: Record<string, unknown>[] }>(
    `/api/anomalies?limit=${limit}&offset=${offset}`
  );

  const items = data.items.map((item) => {
    let rawLog: Record<string, unknown> = {};
    if (typeof item.raw_log === "string") {
      try {
        rawLog = JSON.parse(item.raw_log) as Record<string, unknown>;
      } catch {
        rawLog = {};
      }
    }
    return mapAnomaly(rawLog);
  });

  return { total: data.total, items };
}

export async function uploadLogs(file: File): Promise<DetectAnomaliesResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const data = await request<{
    total_logs: number;
    anomalies_detected: number;
    incident_report: Record<string, unknown>;
    incident_summary: string;
    anomalies: Record<string, unknown>[];
  }>("/api/anomalies/detect", {
    method: "POST",
    body: formData
  });

  return {
    ...data,
    anomalies: data.anomalies.map(mapAnomaly)
  };
}
