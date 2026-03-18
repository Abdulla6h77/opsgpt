import Link from "next/link";
import { Incident } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";

interface IncidentTableProps {
  incidents: Incident[];
  page: number;
  pageSize: number;
  total: number;
  onPageChange?: (nextPage: number) => void;
}

function severityVariant(severity: Incident["severity"]) {
  if (severity === "CRITICAL") return "critical";
  if (severity === "HIGH") return "high";
  if (severity === "MEDIUM") return "medium";
  return "low";
}

export function IncidentTable({
  incidents,
  page,
  pageSize,
  total,
  onPageChange
}: IncidentTableProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="rounded-lg border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Incident ID</TableHead>
            <TableHead>Service</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Summary</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {incidents.map((incident) => (
            <TableRow key={incident.id}>
              <TableCell className="font-mono text-xs">{incident.id.slice(0, 8)}...</TableCell>
              <TableCell>{incident.service}</TableCell>
              <TableCell>
                <Badge variant={severityVariant(incident.severity)}>{incident.severity}</Badge>
              </TableCell>
              <TableCell className="max-w-md truncate">{incident.summary}</TableCell>
              <TableCell>{new Date(incident.created_at).toLocaleString()}</TableCell>
              <TableCell>
                <Link
                  href={`/incidents/${incident.id}`}
                  className="inline-flex h-8 items-center rounded-md border border-border px-3 text-xs hover:bg-accent"
                >
                  View
                </Link>
              </TableCell>
            </TableRow>
          ))}
          {incidents.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground">
                No incidents found.
              </TableCell>
            </TableRow>
          ) : null}
        </TableBody>
      </Table>
      {onPageChange ? (
        <div className="flex items-center justify-between border-t border-border p-3">
          <p className="text-xs text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
