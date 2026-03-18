import { Anomaly } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AnomalyListProps {
  anomalies: Anomaly[];
}

function severityVariant(severity: Anomaly["severity"]) {
  if (severity === "CRITICAL") return "critical";
  if (severity === "HIGH") return "high";
  if (severity === "MEDIUM") return "medium";
  return "low";
}

export function AnomalyList({ anomalies }: AnomalyListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Anomaly List</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {anomalies.length === 0 ? (
            <p className="text-sm text-muted-foreground">No anomalies found for this incident.</p>
          ) : null}
          {anomalies.map((anomaly, index) => (
            <div key={`${anomaly.timestamp}-${index}`} className="rounded-md border border-border bg-muted/20 p-3">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <Badge variant={severityVariant(anomaly.severity)}>{anomaly.severity}</Badge>
                <span className="text-xs text-muted-foreground">{new Date(anomaly.timestamp).toLocaleString()}</span>
                <span className="rounded-md bg-accent px-2 py-0.5 text-xs">{anomaly.service}</span>
              </div>
              <p className="text-sm">{anomaly.message || "No message available."}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                latency={anomaly.latency_ms}ms | status={anomaly.status_code}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

