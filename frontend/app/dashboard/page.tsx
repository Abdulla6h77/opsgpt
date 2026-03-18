"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, BarChart3, Layers3, ShieldAlert } from "lucide-react";
import { fetchAnomalies, fetchIncidents } from "@/lib/api";
import { Incident, IncidentSummary } from "@/lib/types";
import { MetricCard } from "@/components/metric-card";
import { IncidentsChart } from "@/components/charts/incidents-chart";
import { SeverityChart } from "@/components/charts/severity-chart";
import { IncidentTable } from "@/components/incident-table";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent } from "@/components/ui/card";

export default function DashboardPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [anomaliesTotal, setAnomaliesTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [incidentData, anomaliesData] = await Promise.all([fetchIncidents(50, 0), fetchAnomalies(100, 0)]);
        setIncidents(incidentData.items);
        setTotal(incidentData.total);
        setAnomaliesTotal(anomaliesData.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const summary: IncidentSummary = useMemo(() => {
    const critical = incidents.filter((i) => i.severity === "CRITICAL").length;
    const services = new Set(incidents.map((i) => i.service)).size;
    return {
      total_incidents: total,
      critical_incidents: critical,
      services_affected: services,
      total_anomalies: anomaliesTotal
    };
  }, [incidents, total, anomaliesTotal]);

  const severityData = useMemo(() => {
    const levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const;
    return levels.map((level) => ({
      name: level,
      value: incidents.filter((i) => i.severity === level).length
    }));
  }, [incidents]);

  const trendData = useMemo(() => {
    const map = new Map<string, number>();
    incidents.forEach((incident) => {
      const day = new Date(incident.created_at).toLocaleDateString();
      map.set(day, (map.get(day) ?? 0) + 1);
    });
    return [...map.entries()].map(([date, count]) => ({ date, incidents: count }));
  }, [incidents]);

  if (error) {
    return (
      <Alert className="border-red-500/30 bg-red-500/10">
        <AlertTitle>Backend unavailable</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Total Incidents"
          value={loading ? "..." : summary.total_incidents}
          icon={AlertTriangle}
        />
        <MetricCard
          title="Critical Incidents"
          value={loading ? "..." : summary.critical_incidents}
          icon={ShieldAlert}
        />
        <MetricCard
          title="Services Affected"
          value={loading ? "..." : summary.services_affected}
          icon={Layers3}
        />
        <MetricCard
          title="Total Anomalies"
          value={loading ? "..." : summary.total_anomalies}
          icon={BarChart3}
        />
      </section>

      {loading ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">Loading charts...</CardContent>
        </Card>
      ) : (
        <section className="grid gap-4 xl:grid-cols-2">
          <SeverityChart data={severityData} />
          <IncidentsChart data={trendData} />
        </section>
      )}

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Recent Incidents</h2>
        {loading ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">Loading incidents...</CardContent>
          </Card>
        ) : (
          <IncidentTable incidents={incidents.slice(0, 5)} page={1} pageSize={5} total={5} />
        )}
      </section>
    </div>
  );
}

