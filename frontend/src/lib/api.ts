import type { DashboardResponse, Deployment } from "@/lib/types";

const apiUrl = process.env.API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`CloudPulse API returned ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getDashboard(): Promise<DashboardResponse> {
  return getJson<DashboardResponse>("/api/v1/dashboard");
}

export function getDeployments(): Promise<Deployment[]> {
  return getJson<Deployment[]>("/api/v1/deployments");
}
