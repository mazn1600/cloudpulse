import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Dashboard } from "@/components/dashboard";


describe("Dashboard", () => {
  it("renders metrics, service health, and deployment history", () => {
    render(
      <Dashboard
        dashboard={{
          status: "operational",
          metrics: { cpu_percent: 38.4, memory_percent: 62.1, requests_per_minute: 128 },
          services: [{ name: "api", status: "operational" }],
        }}
        deployments={[
          {
            id: 1,
            version: "v0.1.0",
            environment: "local",
            status: "successful",
            deployed_at: "2026-08-17T12:00:00Z",
          },
        ]}
      />
    );

    expect(screen.getByRole("heading", { name: "CloudPulse" })).toBeInTheDocument();
    expect(screen.getByText("38.4%")).toBeInTheDocument();
    expect(screen.getByText("api")).toBeInTheDocument();
    expect(screen.getByText("v0.1.0")).toBeInTheDocument();
  });

  it("renders an explicit empty deployment state", () => {
    render(
      <Dashboard
        dashboard={{
          status: "operational",
          metrics: { cpu_percent: 0, memory_percent: 0, requests_per_minute: 0 },
          services: [],
        }}
        deployments={[]}
      />
    );

    expect(screen.getByText("No deployments recorded.")).toBeInTheDocument();
  });
});
