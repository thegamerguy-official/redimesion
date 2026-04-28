/**
 * REDIMENSION — Shared TypeScript Types.
 *
 * Centralized type definitions used across components and hooks.
 */

/** Application status for the packing workflow state machine. */
export type PackingStatus = "IDLE" | "LOADING" | "SUCCESS" | "ERROR";

/** A single packed item with 3D placement data for the visualizer. */
export interface PackingItem {
  /** Unique identifier (derived from SKU code). */
  id: string;
  /** [width, height, depth] in cm after rotation. */
  dimensions: [number, number, number];
  /** [x, y, z] position within the container (cm). */
  position: [number, number, number];
  /** Optional display color (hex). Defaults to blue. */
  color?: string;
}

/** Complete packing result returned by the engine. */
export interface PackingResult {
  /** Unique order identifier (from barcode scan). */
  orderId: string;
  /** Human-readable box model name (e.g. "CAJA MODELO B"). */
  boxModel: string;
  /** Formatted dimensions string (e.g. "40x30x20 cm"). */
  boxDetails: string;
  /** [width, height, depth] of the selected box in cm. */
  boxDimensions: [number, number, number];
  /** Items placed inside the box with their positions. */
  items: PackingItem[];
}
