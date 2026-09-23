import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "@/app/loading";


describe("Loading", () => {
  it("announces that infrastructure status is loading", () => {
    render(<Loading />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "Loading infrastructure status"
    );
  });
});
