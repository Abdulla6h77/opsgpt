"use client";

import { DragEvent, useMemo, useState } from "react";
import { UploadCloud } from "lucide-react";
import { uploadLogs } from "@/lib/api";
import { DetectAnomaliesResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { RemediationList } from "@/components/remediation-list";

const ACCEPTED = [".log", ".txt"];

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DetectAnomaliesResponse | null>(null);

  const summary = useMemo(() => {
    if (!result) return null;
    const first = result.anomalies[0];
    return {
      rootCause: first?.root_cause ?? "No root cause generated.",
      remediation: first?.suggested_fix ?? "Manual investigation required."
    };
  }, [result]);

  function validateAndSet(input: File | null) {
    if (!input) return;
    const lower = input.name.toLowerCase();
    if (!ACCEPTED.some((ext) => lower.endsWith(ext))) {
      setError("Only .log and .txt files are allowed.");
      return;
    }
    setError(null);
    setFile(input);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    validateAndSet(event.dataTransfer.files?.[0] ?? null);
  }

  async function onUpload() {
    if (!file) return;
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const data = await uploadLogs(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Upload Logs</h1>
        <p className="text-sm text-muted-foreground">Upload log files to run anomaly detection and incident analysis.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Drag and Drop Log File</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={`rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
              dragging ? "border-primary bg-primary/10" : "border-border"
            }`}
          >
            <UploadCloud className="mx-auto mb-2 h-8 w-8 text-primary" />
            <p className="text-sm">Drop a `.log` or `.txt` file here, or pick one manually.</p>
            <input
              className="mx-auto mt-4 block text-xs text-muted-foreground"
              type="file"
              accept=".log,.txt"
              onChange={(e) => validateAndSet(e.target.files?.[0] ?? null)}
            />
            {file ? <p className="mt-2 text-xs text-muted-foreground">Selected: {file.name}</p> : null}
          </div>
          <Button className="mt-4" onClick={onUpload} disabled={!file || submitting}>
            {submitting ? "Analyzing..." : "Upload and Analyze"}
          </Button>
        </CardContent>
      </Card>

      {error ? (
        <Alert className="border-red-500/30 bg-red-500/10">
          <AlertTitle>Upload failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      {result ? (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Result</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>Anomalies detected: {result.anomalies_detected}</p>
              <p>Incident summary: {result.incident_summary}</p>
              <p>Root cause: {summary?.rootCause}</p>
            </CardContent>
          </Card>
          <RemediationList text={summary?.remediation ?? "Manual investigation required."} />
        </div>
      ) : null}
    </div>
  );
}

