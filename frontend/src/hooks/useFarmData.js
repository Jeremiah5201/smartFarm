import { useCallback, useEffect, useState } from "react";
import { api } from "../services/api";

export function useFarmData(farmId) {
  const [data, setData] = useState({ farms: [], latest: null, readings: [], history: [], health: null, latestError: "" });
  const [state, setState] = useState({ loading: true, error: "", refreshing: false });

  const load = useCallback(async (refresh = false) => {
    setState((current) => ({ ...current, loading: !refresh, refreshing: refresh, error: "" }));
    try {
      const [farms, health] = await Promise.all([api.farms(), api.health()]);
      const selectedFarmId = farmId || farms[0]?.farm_id;
      if (!selectedFarmId) {
        setData({ farms, latest: null, readings: [], history: [], health, latestError: "" });
      } else {
        const [latestResult, readings, history] = await Promise.all([
          api.latest(selectedFarmId).then((value) => ({ value, error: "" })).catch((error) => ({ value: null, error: error.message })),
          api.readings(selectedFarmId),
          api.irrigationHistory(selectedFarmId),
        ]);
        setData({ farms, latest: latestResult.value, readings, history, health, latestError: latestResult.error });
      }
    } catch (error) {
      setState((current) => ({ ...current, error: error.message || "Could not reach the backend." }));
    } finally {
      setState((current) => ({ ...current, loading: false, refreshing: false }));
    }
  }, [farmId]);

  useEffect(() => {
    load();
  }, [load]);

  return { ...data, ...state, reload: () => load(true) };
}