export type ServiceStatus = "operational" | "degraded" | "unknown";

export interface MetricSnapshot {
  cpu_percent: number;
  memory_percent: number;
  requests_per_minute: number;
}

export interface ServiceSnapshot {
  name: string;
  status: ServiceStatus;
}

export interface DashboardResponse {
  status: ServiceStatus;
  metrics: MetricSnapshot;
  services: ServiceSnapshot[];
}

export interface Deployment {
  id: number;
  version: string;
  environment: string;
  status: "successful" | "failed" | "running";
  deployed_at: string;
}
