import type { BeamSteeringRequest, BeamSteeringResult, Health, TradeoffRequest, TradeoffResult } from "./types";

const apiBase =
  import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBase}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  } catch {
    throw new Error("Could not reach the simulation server. Check that the backend is running and retry.");
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    const message = Array.isArray(detail) ? detail.map((entry) => entry.msg).join(" ") : detail;
    throw new Error(message || "The simulation server returned an unexpected error.");
  }
  return response.json() as Promise<T>;
}

export const getHealth = () => request<Health>("/api/health");
export const runBeamSteering = (body: BeamSteeringRequest) =>
  request<BeamSteeringResult>("/api/simulations/beam-steering", { method: "POST", body: JSON.stringify(body) });
export const runTradeoff = (body: TradeoffRequest) =>
  request<TradeoffResult>("/api/simulations/tradeoff", { method: "POST", body: JSON.stringify(body) });

