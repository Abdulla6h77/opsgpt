"use client";

import { useEffect, useState } from "react";
import { fetchIncidents } from "@/lib/api";
import { Incident } from "@/lib/types";
import { IncidentTable } from "@/components/incident-table";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent } from "@/components/ui/card";

const PAGE_SIZE = 10;

export default function IncidentsPage() {
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const offset = (page - 1) * PAGE_SIZE;
        const data = await fetchIncidents(PAGE_SIZE, offset);
        setIncidents(data.items);
        setTotal(data.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load incidents.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Incidents</h1>
        <p className="text-sm text-muted-foreground">Paginated incident feed with severity and timeline.</p>
      </div>
      {error ? (
        <Alert className="border-red-500/30 bg-red-500/10">
          <AlertTitle>Failed to fetch incidents</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}
      {loading ? (
        <Card>
          <CardContent className="py-8 text-center text-sm text-muted-foreground">Loading incident table...</CardContent>
        </Card>
      ) : (
        <IncidentTable incidents={incidents} page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
      )}
    </div>
  );
}

