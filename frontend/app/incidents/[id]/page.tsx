"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { fetchAnomalies, fetchIncident } from "@/lib/api";
import { Anomaly, Incident } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AnomalyList } from "@/components/anomaly-list";
import { RemediationList } from "@/components/remediation-list";

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [incident, setIncident] = useState<Incident | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [incidentData, anomaliesData] = await Promise.all([fetchIncident(id), fetchAnomalies(100, 0)]);
        setIncident(incidentData);
        const related = anomaliesData.items.filter((a) => a.service === incidentData.service).slice(0, 20);
        setAnomalies(related);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load incident details.");
      } finally {
        setLoading(false);
      }
    }
    if (id) {
      load();
    }
  }, [id]);

  const rootCause = useMemo(() => incident?.root_cause || "No root cause provided.", [incident]);
  const remediation = useMemo(() => incident?.remediation || "Manual investigation required.", [incident]);

  if (error) {
    return (
      <Alert className="border-red-500/30 bg-red-500/10">
        <AlertTitle>Failed to load incident</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (loading || !incident) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">Loading incident detail...</CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Incident Summary</h1>
        <p className="mt-2 text-sm text-muted-foreground">{incident.summary}</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Root Cause Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{rootCause}</p>
          </CardContent>
        </Card>
        <RemediationList text={remediation} />
      </div>
      <AnomalyList anomalies={anomalies} />
    </div>
  );
}
