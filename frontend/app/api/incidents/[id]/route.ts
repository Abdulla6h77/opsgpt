import { NextResponse } from "next/server";
import { backendRequest } from "@/lib/server-api";

export async function GET(_: Request, context: { params: { id: string } }) {
  const id = context.params.id;
  const response = await backendRequest(`/incidents/${id}`, { method: "GET" });
  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") || "application/json" },
  });
}

