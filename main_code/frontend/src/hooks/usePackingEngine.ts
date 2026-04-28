/**
 * usePackingEngine — Packing Workflow State Machine.
 *
 * Manages the IDLE → LOADING → SUCCESS/ERROR lifecycle for the
 * Pick & Pack interface. Currently uses a mock backend; replace
 * the setTimeout with a real API call when the backend is integrated.
 */

import { useState, useCallback } from "react";

import type { PackingStatus, PackingResult } from "../types";

/** Simulated API latency in milliseconds. */
const MOCK_LATENCY_MS = 600;

export function usePackingEngine() {
  const [status, setStatus] = useState<PackingStatus>("IDLE");
  const [result, setResult] = useState<PackingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchOrderPacking = useCallback((orderId: string) => {
    setStatus("LOADING");
    setError(null);
    console.log(`[PackingEngine] Looking up order: ${orderId}`);

    // TODO: Replace with real API call → fetch(`/api/v1/pack/${orderId}`, ...)
    setTimeout(() => {
      if (orderId.includes("ERR")) {
        setStatus("ERROR");
        setError("Pedido no encontrado o dimensiones inválidas.");
      } else {
        setStatus("SUCCESS");
        setResult({
          orderId,
          boxModel: "CAJA MODELO B",
          boxDetails: "40x30x20 cm",
          boxDimensions: [40, 20, 30],
          items: [
            {
              id: "pantalon",
              dimensions: [38, 5, 28],
              position: [0, -7.5, 0],
              color: "#3b82f6",
            },
            {
              id: "camisetas",
              dimensions: [20, 10, 20],
              position: [-9, 0, 0],
              color: "#f59e0b",
            },
            {
              id: "cinturon",
              dimensions: [15, 5, 10],
              position: [10, -2.5, 5],
              color: "#ef4444",
            },
          ],
        });
      }
    }, MOCK_LATENCY_MS);
  }, []);

  const resetState = useCallback(() => {
    setStatus("IDLE");
    setResult(null);
    setError(null);
  }, []);

  return {
    status,
    result,
    error,
    fetchOrderPacking,
    resetState,
  } as const;
}
