const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SECURITY_API_KEY = process.env.SECURITY_API_KEY || "";

export async function backendRequest(path: string, init?: RequestInit): Promise<Response> {
  if (!SECURITY_API_KEY) {
    return new Response(JSON.stringify({ error: "SECURITY_API_KEY is not configured on frontend server." }), {
      status: 500,
      headers: { "content-type": "application/json" },
    });
  }

  const headers = new Headers(init?.headers || {});
  headers.set("X-API-Key", SECURITY_API_KEY);

  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
}
