const BASE = "http://localhost:8000"

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export type SessionState = "idle" | "recording" | "generating" | "ready"

export function startSession(): Promise<{ session_id: string }> {
  return request("/session/start", { method: "POST" })
}

export function stopSession(): Promise<{ message: string }> {
  return request("/session/stop", { method: "POST" })
}

export function getStatus(): Promise<{ state: SessionState }> {
  return request("/session/status")
}

export function getResult(): Promise<{ notion_url: string; documentation_markdown: string }> {
  return request("/session/result")
}
