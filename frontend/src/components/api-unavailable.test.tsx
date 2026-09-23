import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ApiUnavailable } from "@/components/api-unavailable";


describe("ApiUnavailable", () => {
  it("tells the operator what to inspect", () => {
    render(<ApiUnavailable />);

    expect(screen.getByText("API unavailable")).toBeInTheDocument();
    expect(screen.getByText(/port 8000/)).toBeInTheDocument();
    expect(screen.getByText(/backend terminal logs/)).toBeInTheDocument();
  });
});
