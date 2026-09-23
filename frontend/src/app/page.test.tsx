import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Home from "@/app/page";
import { getDashboard, getDeployments } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  getDashboard: vi.fn(),
  getDeployments: vi.fn(),
}));


describe("Home", () => {
  it("shows the unavailable state when the API cannot be reached", async () => {
    vi.mocked(getDashboard).mockRejectedValue(new TypeError("fetch failed"));
    vi.mocked(getDeployments).mockResolvedValue([]);

    render(await Home());

    expect(screen.getByText("API unavailable")).toBeInTheDocument();
  });

  it("shows the dashboard when the API responds", async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      status: "operational",
      metrics: { cpu_percent: 1, memory_percent: 2, requests_per_minute: 3 },
      services: [],
    });
    vi.mocked(getDeployments).mockResolvedValue([]);

    render(await Home());

    expect(screen.getByRole("heading", { name: "CloudPulse" })).toBeInTheDocument();
  });
});
