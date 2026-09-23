import { describe, expect, it, vi } from "vitest";
import { api } from "../src/services/api";

describe("SmartFarm API client", () => {
  it("loads backend health", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ status: "ok" }) }));
    await expect(api.health()).resolves.toEqual({ status: "ok" });
    expect(fetch).toHaveBeenCalledWith("/api/health", expect.anything());
  });

  it("loads farms from the backend", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [{ farm_id: "FARM001" }] }));
    await expect(api.farms()).resolves.toEqual([{ farm_id: "FARM001" }]);
    expect(fetch).toHaveBeenCalledWith("/api/farms", expect.objectContaining({ headers: { "Content-Type": "application/json" } }));
  });

  it("surfaces backend error details", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404, json: async () => ({ detail: "farm not found" }) }));
    await expect(api.latest("UNKNOWN")).rejects.toThrow("farm not found");
  });

  it("uses the live irrigation command route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) }));
    await api.override("FARM001", { pump: true, duration_sec: 30 });
    expect(fetch).toHaveBeenCalledWith("/api/irrigation/FARM001/override", expect.objectContaining({ method: "POST" }));
  });
});