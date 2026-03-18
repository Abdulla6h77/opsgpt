import { NextResponse } from "next/server";
import { backendRequest } from "@/lib/server-api";

export async function POST(request: Request) {
  const formData = await request.formData();
  const response = await backendRequest("/anomalies/detect", {
    method: "POST",
    body: formData,
  });
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") || "application/json" },
  });
}

