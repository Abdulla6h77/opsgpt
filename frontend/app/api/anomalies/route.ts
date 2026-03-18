import { NextRequest, NextResponse } from "next/server";
import { backendRequest } from "@/lib/server-api";

export async function GET(request: NextRequest) {
  const search = request.nextUrl.search || "";
  const response = await backendRequest(`/anomalies${search}`, { method: "GET" });
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") || "application/json" },
  });
}

